#!/bin/bash
#if [ -d /home/ubuntu/upload/Aussie/ARCDiscovery/txt ]; then
#	rm -r txt
#fi
if [ -d txt ]; then
	rm -r txt
fi
mkdir txt

#mkdir txt
#for f in /home/ubuntu/upload/Aussie/ARCDiscovery/*.pdf
for f in ./*.pdf
do
	echo $f
	pdftotext $f
        mv *.txt txt/. 
done

echo "total files: `ls -1 | wc -l`" >> txt/report.txt

find txt/. -size +100c -exec ls -ld {} \;
echo "files with text data: `find txt/. -size +100c -exec ls -ld {} \; | wc -l`" >> txt/report.txt
echo -e "Names of text files:\n`find txt -size +100c -exec ls -m1 {} \;`" >> txt/report.txt
