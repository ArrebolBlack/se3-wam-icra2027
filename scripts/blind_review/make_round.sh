#!/bin/bash
# Build a blind-review package for round N from the current repository.
# usage: make_round.sh N "A=cosmos_policy B=ours C=dapl D=motus E=roman_4d"
set -e
N=$1; ASSIGN=$2
S=/tmp/claude-0/-home-claude/acc36e25-3891-5db7-9489-40dbe4fde1e0/scratchpad
B=$S/blind; R=$S/review_r$N
P=/mnt/user-data/uploads/se3-wam-research/local_private/cvpr_writing_materials_2026_10_13/papers
REPO=/mnt/user-data/outputs/repo
python3 -I $B/make_blind_source.py $REPO $B/src > /dev/null
(cd $B/src && latexmk -pdf -interaction=nonstopmode -halt-on-error paper_full.tex > lmk.txt 2>&1) || { echo "blind build failed"; exit 1; }
python3 -I $B/pdf2blind.py $B/src/paper_full.pdf $B/test/ours.txt
rm -rf $R; mkdir -p $R/submissions
cp -r $S/review_r1/reference_pool $R/reference_pool
for pair in $ASSIGN; do
  k=${pair%%=*}; v=${pair#*=}
  cp $B/test/$v.txt $R/submissions/paper_$k.txt
done
echo "$ASSIGN" > $B/assignment_r$N.txt
wc -w $R/submissions/*.txt
