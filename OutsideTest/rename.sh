#!/bin/bash
echo "Enter file prefix:"
read pref
echo "Enter file suffix:"
read suff
echo "Enter word to add:"
read add
echo "Enter word to remove:"
read rem
for i in {0..9}
do
  mv ${pref}${rem}${suff}${i}.png ${pref}${add}${suff}${i}.png
  echo "moving ${pref}${rem}${suff}${i}.png to ${pref}${add}${suff}${i}.png"
done
