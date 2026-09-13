"""Evaluate additional glucose-shape features using the fixed development folds."""
import json
from pathlib import Path
import numpy as np
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from train import PATIENT_FILES,read_export,GLUCOSE,CARBS,extract_patient,purge_overlaps,metrics
from test import extract_features,fill_sample

SHAPE_NAMES = ['max_15min_rise','min_15min_change','max_30min_rise','min_30min_change',
               'max_60min_rise','min_60min_change','early_slope','late_slope',
               'longest_rise_fraction','longest_fall_fraction','lag1_correlation',
               'rise_after_trough_fraction','peak_above_end','early_relative_rise']


def shape_features(samples):
    base=extract_features(samples)
    extra=[]
    for row in samples:
        x=fill_sample(row); n=len(x)
        values=[]
        for lag in (3,6,12):
            delta=x[lag:]-x[:-lag]
            values.extend([delta.max(),delta.min()])
        for part in np.array_split(x,3)[::2]:
            t=np.arange(len(part))*5
            values.append(np.dot(t-t.mean(),part-part.mean())/np.sum((t-t.mean())**2))
        d=np.diff(x)
        for sign in (1,-1):
            best=run=0
            for step in d*sign:
                run=run+1 if step>0 else 0
                best=max(best,run)
            values.append(best/len(d))
        a=x[:-1]-x[:-1].mean(); b=x[1:]-x[1:].mean()
        denominator=np.linalg.norm(a)*np.linalg.norm(b)
        values.append(float(a@b/denominator) if denominator else 0.)
        trough=int(np.argmin(x)); peak=trough+int(np.argmax(x[trough:]))
        values.extend([(peak-trough)/(n-1),(x.max()-x[-3:].mean())/x[:3].mean(),
                       (x[:n//2].max()-x[:3].mean())/x[:3].mean()])
        extra.append(values)
    return np.column_stack([base,np.asarray(extra)])


def prepare(samples,y,indices,enriched):
    rows,labels,weights=[],[],[]
    counts=np.bincount(y[indices],minlength=2)
    for i in indices:
        x=samples[i]; views=[x] if len(x)==24 else [x,x[:24],x[3:27],x[6:30]]
        rows.extend(views);labels.extend([y[i]]*len(views))
        weights.extend([len(indices)/(2*counts[y[i]]*len(views))]*len(views))
    return (shape_features(rows) if enriched else extract_features(rows)),labels,weights


def fit(prepared,gamma):
    x,y,w=prepared
    return make_pipeline(StandardScaler(),SVC(C=1,kernel='rbf',gamma=gamma)).fit(
        x,y,standardscaler__sample_weight=w,svc__sample_weight=w)


def main():
    samples,labels,groups,starts,patients=[],[],[],[],[]
    for patient,(cgm,insulin) in enumerate(PATIENT_FILES,1):
        batch,y,g,times,_=extract_patient(read_export(cgm,GLUCOSE),read_export(insulin,CARBS),patient)
        samples.extend(batch);labels.extend(y);groups.extend(g);starts.extend(times);patients.extend([patient]*len(y))
    y=np.array(labels);patients=np.array(patients)
    configs={'baseline':(False,'scale'),'shape':(True,'scale'),'shape_gamma_001':(True,0.01)}
    views={enriched:{str(offset):(shape_features if enriched else extract_features)([x[offset:offset+24] if len(x)==30 else x for x in samples]) for offset in (0,3,6)} for enriched in (False,True)}
    pred={name:{view:np.zeros(len(y),dtype=int) for view in ('0','3','6')} for name in configs}
    cv=StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=572)
    for fold,(training,validation) in enumerate(cv.split(views[False]['0'],y,groups),1):
        training=purge_overlaps(training,validation,starts,samples,patients)
        prepared={v:prepare(samples,y,training,v) for v in (False,True)}
        for name,(enriched,gamma) in configs.items():
            machine=fit(prepared[enriched],gamma)
            for view in pred[name]:
                pred[name][view][validation]=machine.predict(views[enriched][view][validation])
        print('Completed shape fold',fold,flush=True)
    results={}
    for name,(enriched,gamma) in configs.items():
        results[name]={'out_of_fold':{v:metrics(y,p) for v,p in pred[name].items()},'patient_holdout':{}}
        for patient in (1,2):
            held=patients==patient
            machine=fit(prepare(samples,y,np.flatnonzero(~held),enriched),gamma)
            results[name]['patient_holdout'][str(patient)]=metrics(y[held],machine.predict(views[enriched]['0'][held]))
        print(name,results[name],flush=True)
    Path('shape_comparison.json').write_text(json.dumps({'notes':'Fixed development comparisons, same purged folds. No hidden labels. No untouched test claim.','feature_names':SHAPE_NAMES,'results':results},indent=2)+'\n')


if __name__=='__main__':
    main()
