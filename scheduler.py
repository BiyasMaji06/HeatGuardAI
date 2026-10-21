from collections import deque

def _prepare(processes):
    prepared = []
    seen = set()
    for p in processes:
        item = dict(p)
        pid = str(item["process_id"])
        if pid in seen:
            raise ValueError(f"Duplicate process ID: {pid}")
        seen.add(pid)
        item["process_id"] = pid
        item["arrival_time"] = int(item["arrival_time"])
        item["burst_time"] = int(item["burst_time"])
        item["priority"] = int(item.get("priority", 4))
        if item["arrival_time"] < 0 or item["burst_time"] <= 0:
            raise ValueError("Arrival time must be non-negative and burst time must be positive.")
        item["_input_order"] = len(prepared)
        prepared.append(item)
    return prepared

def _finalize(processes, first_start, completion, timeline):
    results = []
    for p in processes:
        pid = p["process_id"]
        results.append({
            **{k:v for k,v in p.items() if not k.startswith("_")},
            "start_time": first_start[pid],
            "completion_time": completion[pid],
            "response_time": first_start[pid] - p["arrival_time"],
        })
    results.sort(key=lambda p: next(i for i,x in enumerate(processes) if x["process_id"] == p["process_id"]))
    return results, timeline

def _append(timeline, pid, start, end):
    if end <= start: return
    if timeline and timeline[-1]["process_id"] == pid and timeline[-1]["end"] == start:
        timeline[-1]["end"] = end
    else:
        timeline.append({"process_id": pid, "start": start, "end": end})

def fcfs(processes):
    ps = sorted(_prepare(processes), key=lambda p:(p["arrival_time"],p["_input_order"]))
    time = 0; first={}; done={}; timeline=[]
    for p in ps:
        if time < p["arrival_time"]:
            _append(timeline,"IDLE",time,p["arrival_time"]); time=p["arrival_time"]
        pid=p["process_id"]; first[pid]=time; time += p["burst_time"]; done[pid]=time
        _append(timeline,pid,first[pid],time)
    return _finalize(ps,first,done,timeline)

def sjf(processes):
    ps = _prepare(processes); remaining={p["process_id"]:p["burst_time"] for p in ps}
    time=0; first={}; done={}; timeline=[]; finished=set()
    while len(finished)<len(ps):
        ready=[p for p in ps if p["process_id"] not in finished and p["arrival_time"]<=time]
        if not ready:
            nxt=min(p["arrival_time"] for p in ps if p["process_id"] not in finished)
            _append(timeline,"IDLE",time,nxt); time=nxt; continue
        p=min(ready,key=lambda x:(x["burst_time"],x["arrival_time"],x["_input_order"]))
        pid=p["process_id"]; first[pid]=time; time+=p["burst_time"]; done[pid]=time; finished.add(pid); _append(timeline,pid,first[pid],time)
    return _finalize(ps,first,done,timeline)

def srtf(processes):
    ps=_prepare(processes); rem={p["process_id"]:p["burst_time"] for p in ps}
    time=0; first={}; done={}; timeline=[]; finished=set()
    while len(finished)<len(ps):
        ready=[p for p in ps if p["process_id"] not in finished and p["arrival_time"]<=time and rem[p["process_id"]]>0]
        if not ready:
            nxt=min(p["arrival_time"] for p in ps if p["process_id"] not in finished and rem[p["process_id"]]>0)
            _append(timeline,"IDLE",time,nxt); time=nxt; continue
        p=min(ready,key=lambda x:(rem[x["process_id"]],x["arrival_time"],x["_input_order"]))
        pid=p["process_id"]
        if pid not in first: first[pid]=time
        _append(timeline,pid,time,time+1)
        rem[pid]-=1; time+=1
        if rem[pid]==0:
            done[pid]=time; finished.add(pid)
    return _finalize(ps,first,done,timeline)

def priority_scheduling(processes):
    ps=_prepare(processes); time=0; first={}; done={}; timeline=[]; finished=set()
    while len(finished)<len(ps):
        ready=[p for p in ps if p["process_id"] not in finished and p["arrival_time"]<=time]
        if not ready:
            nxt=min(p["arrival_time"] for p in ps if p["process_id"] not in finished)
            _append(timeline,"IDLE",time,nxt); time=nxt; continue
        p=min(ready,key=lambda x:(x["priority"],x["arrival_time"],x["_input_order"]))
        pid=p["process_id"]; first[pid]=time; time+=p["burst_time"]; done[pid]=time; finished.add(pid); _append(timeline,pid,first[pid],time)
    return _finalize(ps,first,done,timeline)

def round_robin(processes, quantum=2):
    if int(quantum) <= 0: raise ValueError("Time quantum must be positive.")
    ps=sorted(_prepare(processes),key=lambda p:(p["arrival_time"],p["_input_order"]))
    rem={p["process_id"]:p["burst_time"] for p in ps}; first={}; done={}; timeline=[]
    q=deque(); idx=0; time=0
    while idx<len(ps) or q:
        if not q and idx<len(ps) and time<ps[idx]["arrival_time"]:
            _append(timeline,"IDLE",time,ps[idx]["arrival_time"]); time=ps[idx]["arrival_time"]
        while idx<len(ps) and ps[idx]["arrival_time"]<=time:
            q.append(ps[idx]); idx+=1
        if not q: continue
        p=q.popleft(); pid=p["process_id"]
        if pid not in first: first[pid]=time
        run=min(int(quantum),rem[pid]); start=time; time+=run; rem[pid]-=run
        _append(timeline,pid,start,time)
        while idx<len(ps) and ps[idx]["arrival_time"]<=time:
            q.append(ps[idx]); idx+=1
        if rem[pid]>0: q.append(p)
        else: done[pid]=time
    return _finalize(ps,first,done,timeline)

shortest_job_first = sjf
shortest_remaining_time_first = srtf
non_preemptive_priority = priority_scheduling