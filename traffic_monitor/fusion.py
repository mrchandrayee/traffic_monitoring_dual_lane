from .geometry import box_iou,center
def merge_rider_and_motorcycle(boxes,confs,cls_ids,track_ids,names,threshold=0.02):
    # Merge person/rider detection with overlapping motorcycle detection into one unit.
    items=[]
    for i,b in enumerate(boxes):
        cid=int(cls_ids[i]); name=str(names.get(cid,cid)).lower()
        items.append({'box':list(map(float,b)),'conf':float(confs[i]),'class_name':name,
                      'track_id':track_ids[i] if track_ids else None,'class_id':cid})
    motos=[i for i,x in enumerate(items) if x['class_name'] in ('motorcycle','motorbike')]
    people=[i for i,x in enumerate(items) if x['class_name']=='person']
    used=set(); result=[]
    for mi in motos:
        m=items[mi]; x1,y1,x2,y2=m['box']; best=None; score=0
        for pi in people:
            if pi in used: continue
            p=items[pi]; cx,cy=center(p['box'])
            expanded=(x1-.25*(x2-x1),y1-.9*(y2-y1),x2+.25*(x2-x1),y2+.15*(y2-y1))
            inside=expanded[0]<=cx<=expanded[2] and expanded[1]<=cy<=expanded[3]
            s=max(box_iou(m['box'],p['box']),0.03 if inside else 0)
            if s>score: best,score=pi,s
        if best is not None and score>=threshold:
            p=items[best]; used.add(best)
            a,b,c,d=m['box']; e,f,g,h=p['box']
            m['box']=[min(a,e),min(b,f),max(c,g),max(d,h)]
            m['conf']=max(m['conf'],p['conf'])
        result.append(m)
    for i,x in enumerate(items):
        if i not in motos and i not in used: result.append(x)
    return result
