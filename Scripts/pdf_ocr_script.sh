#!/bin/bash
file=`pwd`
#/home/pete/Desktop/Bardsley
pdfin="*.pdf"
pdf1="burst"
pdf2="output"
pdfo="$file/burst/%04d.pdf"
imgo="$file/image/"

if [ -d $file ];        then
        rm -rf $file/burst
fi
mkdir "burst"

if [ -d $file/image ];  then
        rm -rf $file/image
fi
mkdir "image"

pdftk $pdfin $pdf1 $pdf2 $pdfo
page=0
for f in $file/burst/*
do
        fname=$(basename "$f")
        oname="$imgo${fname%.*}.jpg"
        oname2="$imgo${fname%.*}.jpeg"
        oname3="$imgo${fname%.*}.png"
#       echo $oname
#        convert $f -density 600 $oname
#        convert $f -density 600 $oname2
#        convert $f -density 600 $oname3
	gs -dNOPAUSE -dBATCH -sDEVICE=pngalpha -sOutputFile=$oname3 -r300 $f
done

