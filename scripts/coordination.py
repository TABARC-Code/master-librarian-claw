#!/usr/bin/env python3
"""Persistent local task and referral queue. No model calls or file modifications."""
import argparse
import json
import sqlite3
import sys
from pathlib import Path
from uuid import uuid4

SCHEMA=Path(__file__).resolve().parents[1]/'catalogue'/'schema_v2.sql'
AGENTS=frozenset(('master-librarian','dewey-classifier','bibliographic-cataloguer','media-archivist','gaming-curator','digital-asset-manager','software-archivist','file-forensics','knowledge-architect','office-manager','collections-auditor','methods-researcher'))
class CoordinationError(ValueError): pass

def check_agent(name):
    if name not in AGENTS: raise CoordinationError('Unknown agent')

def connect(path):
    if not Path(path).is_file(): raise CoordinationError('Catalogue not found')
    db=sqlite3.connect(str(path),timeout=5)
    db.row_factory=sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    if db.execute('PRAGMA user_version').fetchone()[0]!=2:
        db.close();raise CoordinationError('Expected schema v2; migrate first')
    return db

def migrate(path):
    if not Path(path).is_file(): raise CoordinationError('Initialise v1 catalogue first')
    db=sqlite3.connect(str(path),timeout=5)
    try:
        db.execute('PRAGMA foreign_keys=ON')
        version=db.execute('PRAGMA user_version').fetchone()[0]
        if version==2:return False
        if version!=1:raise CoordinationError('Unsupported schema version')
        db.executescript('BEGIN IMMEDIATE;\n'+SCHEMA.read_text(encoding='utf-8')+
            '\nINSERT INTO schema_version(version) VALUES(2);\nPRAGMA user_version=2;\nCOMMIT;')
        return True
    except Exception:
        if db.in_transaction:db.rollback()
        raise
    finally:db.close()

def event(db,task,action,actor,details=None):
    db.execute('INSERT INTO agent_events(task_id,action,actor,details_json) VALUES(?,?,?,?)',
               (task,action,actor,json.dumps(details or {})))

def create(path,title,owner='master-librarian'):
    check_agent(owner)
    if not title or not title.strip():raise CoordinationError('Title required')
    ident=uuid4().hex
    with connect(path) as db:
        db.execute('INSERT INTO agent_tasks(id,title,owner) VALUES(?,?,?)',(ident,title.strip(),owner))
        event(db,ident,'created',owner)
    return ident

def claim(path,task,agent):
    check_agent(agent)
    with connect(path) as db:
        db.execute('BEGIN IMMEDIATE')
        n=db.execute("UPDATE agent_tasks SET status='claimed',claimed_by=?,updated_at=CURRENT_TIMESTAMP WHERE id=? AND status='queued' AND owner=?",(agent,task,agent)).rowcount
        if not n:raise CoordinationError('Task unavailable')
        event(db,task,'claimed',agent)

def refer(path,task,source,target,question):
    check_agent(source);check_agent(target)
    if source==target:raise CoordinationError('Self-referral')
    if not isinstance(question,str) or not question.strip():raise CoordinationError('Question required')
    key=' '.join(question.casefold().split())
    with connect(path) as db:
        db.execute('BEGIN IMMEDIATE')
        row=db.execute('SELECT status,owner,claimed_by FROM agent_tasks WHERE id=?',(task,)).fetchone()
        if row is None or row['status'] not in ('claimed','review'):raise CoordinationError('Inactive task')
        hops=db.execute('SELECT target,response_status FROM agent_referrals WHERE task_id=? ORDER BY id',(task,)).fetchall()
        if len(hops)>=8:raise CoordinationError('Hop limit')
        expected=hops[-1]['target'] if hops else (row['claimed_by'] or row['owner'])
        if source!=expected:raise CoordinationError('Disconnected referral')
        if hops and hops[-1]['response_status']=='pending':raise CoordinationError('Pending response')
        if db.execute('SELECT 1 FROM agent_referrals WHERE task_id=? AND source=? AND target=? AND question_key=?',(task,source,target,key)).fetchone():
            raise CoordinationError('Repeated referral')
        db.execute('INSERT INTO agent_referrals(task_id,source,target,question,question_key) VALUES(?,?,?,?,?)',(task,source,target,question.strip(),key))
        event(db,task,'referred',source,{'target':target})

def respond(path,task,agent,answer):
    check_agent(agent)
    if not isinstance(answer,str) or not answer.strip():raise CoordinationError('Answer required')
    with connect(path) as db:
        db.execute('BEGIN IMMEDIATE')
        hop=db.execute('SELECT id,target,response_status FROM agent_referrals WHERE task_id=? ORDER BY id DESC LIMIT 1',(task,)).fetchone()
        if hop is None or hop['target']!=agent or hop['response_status']!='pending':
            raise CoordinationError('No pending referral')
        db.execute("UPDATE agent_referrals SET response=?,response_status='answered' WHERE id=?",(answer.strip(),hop['id']))
        event(db,task,'answered',agent)

def finish(path,task,actor,status='review'):
    check_agent(actor)
    if status not in ('review','completed','failed','cancelled'):raise CoordinationError('Invalid status')
    with connect(path) as db:
        db.execute('BEGIN IMMEDIATE')
        row=db.execute('SELECT status,owner,claimed_by FROM agent_tasks WHERE id=?',(task,)).fetchone()
        if not row or row['status'] not in ('claimed','review'):raise CoordinationError('Inactive task')
        if actor not in (row['owner'],row['claimed_by'],'master-librarian'):raise CoordinationError('Not authorised')
        if status=='completed' and (actor!='master-librarian' or row['status']!='review'):
            raise CoordinationError('Completion requires Master Librarian review')
        n=db.execute("SELECT count(*) FROM agent_referrals WHERE task_id=? AND response_status='pending'",(task,)).fetchone()[0]
        if n and status in ('review','completed'):raise CoordinationError('Unanswered referral')
        db.execute('UPDATE agent_tasks SET status=?,updated_at=CURRENT_TIMESTAMP WHERE id=?',(status,task))
        event(db,task,status,actor)

def show(path,task):
    with connect(path) as db:
        item=db.execute('SELECT * FROM agent_tasks WHERE id=?',(task,)).fetchone()
        if not item:raise CoordinationError('Missing task')
        refs=db.execute('SELECT source,target,question,response,response_status FROM agent_referrals WHERE task_id=? ORDER BY id',(task,)).fetchall()
        return {'task':dict(item),'referrals':[dict(x) for x in refs]}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--db',required=True)
    sub=p.add_subparsers(dest='cmd',required=True)
    sub.add_parser('migrate')
    x=sub.add_parser('create');x.add_argument('title')
    x=sub.add_parser('claim');x.add_argument('task');x.add_argument('agent')
    x=sub.add_parser('refer');x.add_argument('task');x.add_argument('source');x.add_argument('target');x.add_argument('question')
    x=sub.add_parser('respond');x.add_argument('task');x.add_argument('agent');x.add_argument('answer')
    x=sub.add_parser('finish');x.add_argument('task');x.add_argument('actor');x.add_argument('--status',default='review',choices=['review','completed','failed','cancelled'])
    x=sub.add_parser('show');x.add_argument('task')
    a=p.parse_args()
    try:
        if a.cmd=='migrate':print('Migrated' if migrate(a.db) else 'Already migrated')
        elif a.cmd=='create':print(create(a.db,a.title))
        elif a.cmd=='claim':claim(a.db,a.task,a.agent)
        elif a.cmd=='refer':refer(a.db,a.task,a.source,a.target,a.question)
        elif a.cmd=='respond':respond(a.db,a.task,a.agent,a.answer)
        elif a.cmd=='finish':finish(a.db,a.task,a.actor,a.status)
        elif a.cmd=='show':print(json.dumps(show(a.db,a.task),indent=2))
    except (CoordinationError,sqlite3.Error,OSError) as exc:
        print(str(exc),file=sys.stderr);return 1
    return 0
if __name__=='__main__':raise SystemExit(main())
