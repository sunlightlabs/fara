from pyPdf import PdfFileReader
import codecs
import os

def getDocData(Fdoc):
    from pyPdf import PdfFileReader
    import codecs

    f = PdfFileReader(file(Fdoc, "rb"))
    pages = f.getNumPages()
    pages = int(pages - 1)
    name = Fdoc.replace("input_PDF", "output_text")[:-4] + ".txt"
    
#I want to replace test 2 with something dynamic so I am not writing over my files
    g = codecs.open(name, encoding='utf-8', mode='wb')

    #looping through the pages and putting the contents in to a text document
    l = 0
    for t in range(0, pages):
        while l <= pages:
            pg = f.getPage(l)
            pgtxt = pg.extractText()
            l = l + 1
            g.write(pgtxt)
            #this saves to FARAland

for file_tuple in os.walk(os.getcwd() + "/input_PDF"):
    files = file_tuple[2]
    #loops through files
    for f in files:
        if f[-4:] == ".pdf":
            file_name = "input_PDF/" + f
            print file_name
            getDocData(file_name) 

print "worked"