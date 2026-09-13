"""Compare fixed crop/feature strategies on identical purged validation folds."""
import json
from pathlib import Path

import numpy as np
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, FunctionTransformer
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedGroupKFold

from train import (PATIENT_FILES, GLUCOSE, CARBS, read_export, extract_patient,
                   purge_overlaps, metrics)
from test import extract_features

CONFIGS = {
    'baseline': ('mixed', 'all'),
    '24_only': ('three', 'all'),
    'seven_crops': ('seven', 'all'),
    '24_without_mean': ('three', 'without_mean'),
    '24_selected_12': ('three', 'best12'),
    'mixed_selected_12': ('mixed', 'best12'),
}


def prepare(samples, labels, indices, crop):
    rows, targets, weights = [], [], []
    counts = np.bincount(labels[indices], minlength=2)
    for i in indices:
        x = samples[i]
        if len(x) == 24:
            variants = [x]
        elif crop == 'mixed':
            variants = [x, x[:24], x[3:27], x[6:30]]
        else:
            offsets = range(7) if crop == 'seven' else (0, 3, 6)
            variants = [x[offset:offset+24] for offset in offsets]
        rows.extend(variants)
        targets.extend([labels[i]] * len(variants))
        weights.extend([len(indices)/(2*counts[labels[i]]*len(variants))]*len(variants))
    return extract_features(rows), targets, weights


def fit(prepared, selection):
    features, targets, weights = prepared
    steps = [StandardScaler()]
    if selection == 'best12':
        steps.append(SelectKBest(f_classif, k=12))
    elif selection == 'without_mean':
        steps.append(FunctionTransformer(np.take, kw_args={'indices':list(range(1,24)), 'axis':1}))
    steps.append(SVC(C=1.0, kernel='rbf'))
    model = make_pipeline(*steps)
    return model.fit(features, targets, standardscaler__sample_weight=weights,
                     svc__sample_weight=weights)


def main():
    samples, labels, groups, starts, patients = [], [], [], [], []
    for patient, (cgm, insulin) in enumerate(PATIENT_FILES, 1):
        batch, y, g, times, _ = extract_patient(read_export(cgm, GLUCOSE),read_export(insulin,CARBS),patient)
        samples.extend(batch); labels.extend(y); groups.extend(g); starts.extend(times)
        patients.extend([patient]*len(y))
    y, patients = np.asarray(labels), np.asarray(patients)
    features = {str(offset): extract_features([x[offset:offset+24] if len(x)==30 else x for x in samples])
                for offset in (0,3,6)}
    predictions = {name:{view:np.zeros(len(y),dtype=int) for view in features} for name in CONFIGS}
    results = {name:{'folds':[], 'patient_holdout':{}} for name in CONFIGS}
    cv = StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=572)
    for fold,(training,validation) in enumerate(cv.split(features['0'],y,groups),1):
        training=purge_overlaps(training,validation,starts,samples,patients)
        cache={crop:prepare(samples,y,training,crop) for crop in ('mixed','three','seven')}
        for name,(crop,selection) in CONFIGS.items():
            model=fit(cache[crop],selection)
            for view,matrix in features.items():
                predictions[name][view][validation]=model.predict(matrix[validation])
            score=metrics(y[validation],predictions[name]['0'][validation])
            results[name]['folds'].append({'fold':fold,**score})
        print(f'Completed fold {fold}',flush=True)
    for name,(crop,selection) in CONFIGS.items():
        results[name]['out_of_fold']={view:metrics(y,values) for view,values in predictions[name].items()}
        for patient in (1,2):
            held=patients==patient
            model=fit(prepare(samples,y,np.flatnonzero(~held),crop),selection)
            results[name]['patient_holdout'][str(patient)]=metrics(y[held],model.predict(features['0'][held]))
        print(name,results[name]['out_of_fold']['0'],flush=True)
    report={'notes':'Fixed development comparisons, no hidden labels. Same purged patient/week folds; feature selection, scaling and augmentation fitted inside folds. Not untouched-test estimates.',
            'configurations':CONFIGS,'training_rows':len(y),'results':results}
    Path('representation_comparison.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':
    main()
