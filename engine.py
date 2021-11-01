from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QLineEdit, QTabWidget, QStyle, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QFont,QImage, QPixmap
import sys
import requests
from functools import partial
from client import client, c_print
from resp import response
import socket
import json

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class QVLine(QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)

class HyperlinkLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__()
        #self.setStyleSheet('font-size: 35px')
        self.setOpenExternalLinks(True)
        self.setParent(parent)

class QLabel(QLabel):
    def __init__(self, text='', parent=None):
        super().__init__()
        self.setText(text)
        self.setWordWrap(True)

verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)


class win(QtWidgets.QMainWindow):
  def __init__(self):
    super(win, self).__init__()
    a = QWidget()
    mainbox = QVBoxLayout()
    container = QWidget(self)
    framehead = QHBoxLayout(container)
    container.setStyleSheet("*{background-color=black;}")
    self.searchBar = QLineEdit()
    framehead.addWidget(self.searchBar)
    button = QPushButton('Go', self)
    button.setToolTip('Go to specified address')
    button.clicked.connect(self.go_click)
    framehead.addWidget(button)
    hline = QHLine()
    framehead.addWidget(hline)
    mainbox.addWidget(container)

    self.tabs = QTabWidget()
    self.tabs.tabCloseRequested.connect(self.delete)
    self.tabs.setTabsClosable(True)

    #id = socket.gethostbyname('Sensor')
    #tab, name = self.generalTabUI(f"prysm://{id}/index.mp")
    # UX410
    tab, name = self.generalTabUI("prysm://192.168.2.2/",port=5000)
    self.tabs.addTab(tab, name )

    default_side = self.tabs.style().styleHint(
        QStyle.SH_TabBar_CloseButtonPosition, None, self.tabs.tabBar()
    )

    self.tabs.tabBar().setTabButton(0, default_side, None)

    #tabs.addTab(self.generalTabUI(), "Network")
    mainbox.addWidget(self.tabs)
    a.setLayout(mainbox)
    self.setCentralWidget(a)

  def delete(self, index):
    self.tabs.removeTab(index)

  def generalTabUI(self,url,port=0):
    """Create the General page UI."""
    generalTab = QWidget()
    mainbox = QVBoxLayout()
#  https://Sample-Prysm-Server.huski3.repl.co/test.mp
    if 'prysm://' in url or 'sample-prysm-server' in url:
        if port != 0:
            port = port
        elif 'prysm://' in url:
            port = 2020
        url = url.replace('prysm://','').replace('https://','')
        host, uri = url.split('/',1)
        # Connect and wait for server details
        c = client(url=uri,port=port)
        # Recieved server details
        r = c.connect(host)
        if type(r) == tuple:
            print('Failed!\n',r[1])
            quit()
        print(json.dumps(r.json,sort_keys=True, indent=4))
        # Send back response
        c.reply_info()
        print('Sent machine info!')
        print('sleeping... Waiting for page info...')
        page = c.recieve_page()
        print("Page length:",len(page))
        if len(page) == 3:
            if page == '404':
                print('Page not found... Flushing...')
                mainbox.addWidget(QLabel("<font size=20>404 - Page not found</font>"))
                mainbox.addWidget(QHLine())
                mainbox.addWidget(QLabel("The page you requested does not exist on this address!"))
                mainbox.addItem(verticalSpacer)
                generalTab.setLayout(mainbox)
                var = '404 | Not Found'
                return generalTab, var
        #print(page)
        with open("pain.html",'w+') as f:
          f.write(page)
        self.setWindowTitle("Prysm Engine | prysm://"+url)
        #mainbox.addLayout(framehead)
        # prysm://Sensor/index.mp
        ## Process here
        p = process('pain.html')
        if p.style_f:
            p.out += f"{p.stylesheet}''')"
        a = QLabel("args")
        loc = locals()
        var = 'Un-named'
        for line in p.out.split('\n'):
            if line:
                try:
                    if '<=>' in line:
                        print('>>>',line.replace('<=>','='))
                        if line[:len('[proc_e]')] == '[proc_e]':
                            x = exec(line.replace('<=>','=').replace('[proc_e]',''),globals(),loc)
                        else:
                            x = exec(line.replace('<=>','='),globals(),loc)
                        if 'ret' in loc:
                            mainbox.addWidget(loc['ret'])
                        elif 'reqt' in loc:
                            var = loc['reqt']
                        elif '[ITEM]' in line:
                            mainbox.addItem(x)
                        #print(loc)
                    else:
                        if line[:len('[ITEM]')] == '[ITEM]':
                            print('ITEM')
                            x = eval(line.replace('<=>','=').replace('[ITEM]',''),globals(),loc)
                        else:
                            x = eval(line)
                            if x is not None:
                                mainbox.addWidget(x)
                except Exception as e:
                    print('Failed to process due to ',e)
                    print('Line:',line.replace('<=>','=').replace('[proc]','').replace('[ITEM]',''),)
                    quit()
                #print('processed:',line)
            else:
                print('Incorrect line?',line)
        print('Actual out:\n',p.out)
        generalTab.setLayout(mainbox)
        # Remove later
        #mainbox.setTabToolTip(url)
        return generalTab, var

  def go_click(self):
      url = self.searchBar.text()
      print('User tried to access:',url)
      tab, name = self.generalTabUI(url)
      self.tabs.addTab(tab, name )

  def clicked(self,url):
      print('User tried to access:',url)
      #self.dialog = Second(url=url)
      #self.dialog.show()
      tab, name = self.generalTabUI(url)
      self.tabs.addTab(tab, name )

types = {
  'title':{'code':'QLabel("<font size=30>args</font>")','args':True},
  'p':{'code':'QLabel("args")','args':True},
  'h1':{'code':'QLabel("<font size=20>args</font>")','args':True},
  'h2':{'code':'QLabel("<font size=15>args</font>")','args':True},
  'tc':{'code':'QLabel("<font size=arg2>arg1</font>")','args':True,'margs':True},
  'a':{'code':'''[proc]x <=> QLabel('<a href="arg2">arg1</a>'); x.setToolTip('arg2'); x.linkActivated.connect(partial(self.clicked,'arg2')); ret = x''','args':True,'margs':True,'ext_code':''''''},
  'lh':{'code':'QHLine()','args':True},
  'lv':{'code':'QVLine()','args':True},
  'vs':{'code':'[ITEM]QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)','args':True},
  'page_name':{'code':'[proc_e]page_name <=> "args"; reqt = page_name; print(reqt)','args':True},
  'img':{'code':'''[proc]x <=> QImage(); x.loadFromData(requests.get("arg2").content); image_label <=> QLabel(); image_label.setPixmap(QPixmap(x)); x <=> image_label; x.setToolTip('arg1')  ; ret = image_label''','args':True,'margs':True,'ext_code':''''''},
}
symbols = ['>']
class process:
  def __init__(self,file):
    self.file = file
    self.flags = {
      'r':False,
      'mr':False,
      'b':0
    }
    self.style_f = False
    self.stylesheet = ''
    self.locals = {}
    self.temp_box = ""
    self.box_type = ""
    self.temp = ""
    self.temp2 = ""
    self.temp_kind = ""
    self.out = ""
    self.temp_dict = {}
    self.data = open(self.file,'r').read().replace('\n',' ').split(' ')
    for i,word in enumerate(self.data):
      self._pword(word,i)
    self.process_css()
  def process_css(self):
    self.stylesheet = self.stylesheet.replace('.text','.QLabel').replace('.frame','.QWidget')
  def _pword(self,word,index):
    if self.style_f:
      print(word,end=' ')
      if word.strip():
          self.stylesheet += word+' '
    elif ';' in word and self.flags['r'] == True:
      word = word.strip(';')
      self.temp+=str(word)
      self.flags['r'] = False
      self.temp_kind = self.temp_kind.replace('args',self.temp)
      #print(self.temp_kind)
      if self.flags['b']:
          self.temp_box += self.temp_kind+'\n'
      else:
          self.out += self.temp_kind+'\n'
      self.temp = ""
      self.temp_kind = ""
    elif ';' in word and self.flags['mr'] == True:
      word = word.strip(';')
      self.temp2+=str(word)
      self.flags['mr'] = False
      if 'ext_code' in self.temp_dict:
        ext = self.temp_dict['ext_code'].replace('arg1',self.temp).replace('darg1','_'.join(self.temp.split(' '))).replace('arg2',self.temp2)
        self.temp_kind = self.temp_kind.replace('arg1',self.temp).replace('darg1','_'.join(self.temp.split(' '))).replace('arg2',self.temp2)
        self.out += ext+'\n'
      else:
        self.temp_kind = self.temp_kind.replace('arg1',self.temp).replace('arg2',self.temp2)
      #print(self.temp_kind)
      if self.flags['b']:
          self.temp_box += self.temp_kind+'\n'
      else:
          self.out += self.temp_kind+'\n'
      self.temp = ""
      self.temp2 = ""
      self.temp_kind = ""
      self.temp_dict = {}
    elif word.strip(';') == '>' and self.data[index-1] in types:
      self.temp_dict = types[self.data[index-1]]
      out = types[self.data[index-1]]
      if out['args'] == True:
        self.flags['r'] = True
        self.temp_kind = out['code']
        if 'margs' in out:
          self.flags['mr'] = True
    elif word == '>>' and self.flags['mr'] == True:
      self.temp = self.temp2
      self.temp2 = ' '
      self.flags['r'] = False
    elif word.strip(';') == 'style':
        print('Style triggered! Rest of the file assumed to be css')
        self.style_f = True
        self.out += "\ngeneralTab.setStyleSheet('''"
    elif word == 'box':
        #print('Box layout of type',self.data[index+1].strip(';'),'requested')
        self.flags['b'] += 1
        b = self.flags['b']
        self.box = word+' '+self.data[index+1]
        self.box_type = self.data[index+1].strip(';')
        if self.box_type == 'v':
            self.out += f'temp_layout{b} <=> QVBoxLayout()\n'
        elif self.box_type == 'h':
            self.out += f'temp_layout{b} <=> QHBoxLayout()\n'
        else:
            print('Not a valid type of box, couldnt proces :/ Rechecking!')
            if self.box.strip(';').strip('box').strip() == 'v':
                self.out += f'temp_layout{b} <=> QVBoxLayout()\n'
            elif self.box.strip(';').strip('box').strip() == 'h':
                self.out += f'temp_layout{b} <=> QHBoxLayout()\n'
        if self.temp_box.strip():
            for line in self.temp_box.strip().split('\n'):
                print('>>>',line)
                if line[:len('[proc]')] == '[proc]':
                    loc = locals()
                    if 'ret' in line:
                        print('RED')
                        self.out += line.replace('[proc]','').split('ret')[0]+f'temp_layout{b-1}.addWidget(x)\n'
                    else:
                        self.out += line.replace('[proc]','')+'\n'
                else:
                    if line:
                        self.out += f'temp_layout{b-1}.addWidget({line})\n'
            self.temp_box = ""
    elif word.strip(';') == 'endbox':
        #print('Box ended, reconfiguring contents...')
        b = self.flags['b']
        print('>>>',f'temp_layout{b} of type ({self.box_type}) ({self.box})')
        for line in self.temp_box.strip().split('\n'):
            print('>>>',line)
            if line[:len('[proc]')] == '[proc]':
                loc = locals()
                if 'ret' in line:
                    print('RED')
                    self.out += line.replace('[proc]','').split('ret')[0]+f'temp_layout{b}.addWidget(x)\n'
                else:
                    self.out += line.replace('[proc]','')+'\n'
            else:
                if line:
                    self.out += f'temp_layout{b}.addWidget({line})\n'
        
        if self.flags['b'] == 1:
            self.out += f'mainbox.addLayout(temp_layout{b})\n'
        else:
            self.out += f'temp_layout{b-1}.addLayout(temp_layout{b})\n'
        self.flags['b'] -= 1
        self.box_type = ''
        self.temp_box = ''
    elif self.flags['mr'] == True:
        self.temp2 += str(word)+' '
    elif self.flags['r'] == True:
        self.temp += str(word)+' '
    #elif word.strip(';') in types:
    #    if types[word.strip(';')]['args'] == False:
    #        self.out += types[word.strip(';')]['code']+'\n'


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    screen_rect = app.desktop().screenGeometry()
    global width, height
    width, height = screen_rect.width(), screen_rect.height()
    window = win()
    window.show()
    app.exec_()