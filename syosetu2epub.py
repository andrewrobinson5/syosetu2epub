import os
import shutil
import zipfile
import tempfile
import sys
import string
from datetime import datetime
import requests
import pytz

cwd = os.getcwd()
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

class SyosetuRequest:
    def __init__(self):
        self.srHeaders = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0'
        }
        self.srCookies = dict(over18='yes')
        self.link = None

    def getResponse(self):
        if self.link[-1] == "/":
            self.link = self.link.rstrip("/")
        r = requests.get(url=self.link, headers=self.srHeaders, cookies=self.srCookies)
        toc = {
            "page": r.text,
            "url": self.link
        }
        return toc

class Novel:
    def __init__(self, novelToc):
        self.chapterCount = 0
        self.tempDir = None
        self.page = novelToc["page"]
        self.link = novelToc["url"]
        self.seriesCode = novelToc["url"].split(".syosetu.com/", 1)[1]
        if "/" in self.seriesCode:
            seriesCode = self.seriesCode.split("/", 1)[0]
        
        # collect author and title metadata
        title = self.page.split("<p class=\"novel_title\">", 1)[1]
        self.title, author = title.split("</p>", 1)
        author = author.split("<div class=\"novel_writername\">\n", 1)[1]
        self.author = author.split("</div>", 1)[0]

        self.outputPath = os.path.join(cwd, self.title)
        appendage = ""
        i = 1
        while os.path.isfile(self.outputPath + appendage + '.epub'):
            appendage = "(" + str(i) + ")"
            i += 1
        self.outputPath = self.outputPath + appendage + '.epub'

    def genTableOfContents(self):
        tocInsert = ""
        tocInsertLegacy = ""
        indexBox = self.page.split("<div class=\"index_box\">", 1)[1]
        indexBox = self.page.split("</div><!--index_box-->", 1)[0]
        for line in indexBox.splitlines():
            if "class=\"chapter_title\"" in line:
                chapter = line.split(">", 1)[1]
                chapter = chapter.split("</div>", 1)[0]
                tocInsert += "<li>" + chapter + "</li>\n"
            elif "<a href=\"/" + self.seriesCode + "/" in line:
                entry = line.split(">", 1)[1]
                entry = entry.split("</a>", 1)[0]
                self.chapterCount+=1
                tocInsert += "<li><a href=\"" + str(self.chapterCount) + ".xhtml\">" + entry + "</a></li>\n"
                tocInsertLegacy += "<navPoint id=\"toc" + str(self.chapterCount) + "\" playOrder=\"" + str(self.chapterCount) + "\"><navLabel><text>" + entry + "</text></navLabel><content src=\"" + str(self.chapterCount) + ".xhtml\"/></navPoint>"
        with open(os.path.join(__location__, 'files/nav.xhtml')) as t:
            template = string.Template(t.read())
            finalOutput = template.substitute(TITLETAG=self.title, TOCTAG=tocInsert)
            oebpsDir = os.path.join(self.tempDir.name, self.title, "OEBPS")
            with open(os.path.join(oebpsDir, "nav.xhtml"), "w") as output:
                output.write(finalOutput)
        with open(os.path.join(__location__, 'files/toc.ncx')) as t:
            template = string.Template(t.read())
            finalOutput = template.substitute(IDTAG=self.seriesCode, TITLETAG=self.title, TOCTAG=tocInsertLegacy)
            oebpsDir = os.path.join(self.tempDir.name, self.title, "OEBPS")
            with open(os.path.join(oebpsDir, "toc.ncx"), "w") as output:
                output.write(finalOutput)

    def genTitlePage(self):
        with open(os.path.join(__location__, 'files/titlepage.xhtml')) as t:
            template = string.Template(t.read())
            finalOutput = template.substitute(TITLETAG=self.title, AUTHORTAG=self.author)
            oebpsDir = os.path.join(self.tempDir.name, self.title, "OEBPS")
            with open(os.path.join(oebpsDir, "titlepage.xhtml"), "w") as output:
                output.write(finalOutput)

    def genBook(self):
        self.tempDir = tempfile.TemporaryDirectory()
        destination = shutil.copytree(os.path.join(__location__, 'template'), os.path.join(self.tempDir.name, self.title))

        self.genTitlePage()
        self.genTableOfContents()

        chapterList = ""
        chapterListAgain = ""
        chapterRequest = SyosetuRequest()
        for i in range(self.chapterCount):
            chapterRequest.link = self.link + "/" + str(i+1)
            thisChapter = chapterRequest.getResponse()
            content = thisChapter["page"].split("<p class=\"novel_subtitle\">", 1)[1]
            title, content = content.split("</p>", 1)
            content = content.split("<div class=\"novel_bn\">", 1)[0]
            chapterText = "<h2 id=\"toc_index_1\">" + title + "</h2>\n"
            for line in content.splitlines():
                if "<br />" in line:
                    continue
                elif "id=\"novel_honbun\"" in line:
                    continue
                elif "id=\"novel_p\"" in line:
                    continue
                elif "</div>" in line:
                    continue
                elif "id=\"novel_a\"" in line:
                    line = "<br />\n"
                elif "<p id=\"L" in line:
                    line = line.split(">", 1)[1]
                    line = line.split("</p>", 1)[0]
                    line = "<p>" + line + "</p>"
                chapterText += line
                chapterText += "\n"
            with open(os.path.join(__location__, 'files/chaptertemplate.xhtml')) as t:
                template = string.Template(t.read())
                finalOutput = template.substitute(TITLETAG=self.title, BODYTAG=chapterText)
                with open(os.path.join(self.tempDir.name, self.title, 'OEBPS', (str(i + 1) + '.xhtml')), "w") as output:
                    output.write(finalOutput)
            chapterList += "<item media-type=\"application/xhtml+xml\" href=\"" + str(i + 1) + ".xhtml""\" id=\"_" + str(i + 1) + ".xhtml\" />"
            chapterListAgain += "<itemref idref=\"_" + str(i + 1) + ".xhtml\" />"

        with open(os.path.join(__location__, 'files/content.opf')) as t:
            template = string.Template(t.read())
            authorName = self.author.split("：", 1)[1]
            if '<a' in authorName:
                authorName = authorName.split(">", 1)[1]
                authorName = authorName.split("<")[0]
            finalOutput = template.substitute(IDTAG=self.seriesCode, TITLETAG=self.title, AUTHORTAG=authorName, TIMESTAMPTAG=datetime.now(pytz.utc).isoformat().split('.', 1)[0] + 'Z', CHAPTERSTAG=chapterList, SPINETAG=chapterListAgain)
            oebpsDir = os.path.join(self.tempDir.name, self.title, "OEBPS")
            with open(os.path.join(oebpsDir, "content.opf"), "w") as output:
                output.write(finalOutput)
        
        with zipfile.ZipFile(self.outputPath, 'w') as zip:
            os.chdir(os.path.join(__location__, 'files'))
            zip.write('mimetype')
            os.chdir(os.path.join(self.tempDir.name, self.title))
            paths = []
            for root, directories, files in os.walk('.'):
                for filename in files:
                    path = os.path.join(root, filename)
                    paths.append(path)
            for doc in paths:
                zip.write(doc)
            os.chdir(__location__)

if __name__ == "__main__":
    myRequest = SyosetuRequest()
    for arg in sys.argv:
        if ".syosetu.com/" in arg:
            myRequest.link = arg
    if myRequest.link == None:
        print("USAGE: syosetu2epub http://*.ncode.com/******")
        print("OUTPUT: EPUB formatted ebook will be generated in current working directory")
        os._exit(0)

    myNovel = Novel(myRequest.getResponse())
    myNovel.genBook()