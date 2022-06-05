# A simple Python script for converting opentype unicode-based
# Tamil characters to glyph format suitable for pasting in
# Affinity programs. You will have to reformat all the
# text in Affinity after pasting the clipboard and toggling
# to unicode. The app converts the Tamil unicode text to
# a string of glyph data that can be displayed inside
# Affinity apps. This works only for certain unicode-based open
# type fonts. The script reads the .ttf file, extracts the cmap and
# GSUB lookup tables and saves them in a temporary .xml file
# for use. If the opentype .ttf font file contains all the
# necessary glyphs for Tamil and if they all are also indexed in
# GSUB lookup tables, this Python program script will work!
#
# Usage: select and copy-paste true-type Tamil text in the upper window,
# press convert, press copy to copy converted format to clipboard
# press clear to clear both screens and the clipboard.
#
# Easiest way to copy the converted data is: open a new Text box
# in Affinity, press 'cmd v' to paste inside, 'cmd a' to select all,
# ctrl u to toggle to unicode, and then change font to the
# correct one.
#
# known problems: only level 1 substitution is ready and so
# it does not display some sanskrit characters like sri or ksha.
# Also char 'vi' in Latha font does not display correctly in Affinity.
#
# Note that copied text inside Affinity is not font
# characters, but glyph characters. So, you won't be able
# to change the font family. But you can resize the characters
# and any minor editing can be done using the glyph browser.
# Only Tamil and English characters are allowed. If you have
# other non-unicode font texts, you will have to convert and
# add them separately. Non-Tamil unicode text is passed through
# the program without conversion. All the formatting in the
# original text is also lost during clip and paste. So, you
# will have to reformat the text after pasting in Affinity.
# Some unicode-based opentype may not display correctly if
# they do not have all the glyph encoded in the GSUB list.
# Fonts like Vijaya, Akshar, TAU-encoded Tamil fonts, and many
# more work well.
#
# In Latha font, chars like 'vi' does not display correctly
# since it depends on GPOS data, and not GSUB. The glyph for this
# character 'vi is not inside .ttf file, and it has to be rendered
# using GPOS table by the Affinity app. It does so somewhat imperfectly,
# but otherwise it's fine.
#
# For other Indic languages, you will have to change some of the data
# inside the section below in this program. Tested up to 20-page
# MS Word Akshar or Vijaya font documents. Google Tamil fonts
# do not work, since they do not depend entirely on psts substitution
# rules in the GSUB table. They use more open-type features. Good luck!
#
# Chakravathy Mathiazhagan, IIT Madras.
#

# update 26 May 2022 -- added support for .ttc font collection files
# fixed a bug that happens when both taml and tml2 versions are present
# update 27 May 2022 -- added checking for GSUB table in font file

# added Hindi support. also added a middle window for showing unicode
# implemented multiple level lookups needed for Hindi
# This is a very messy implementation and there may be bugs when certain
# char combinations are encountered! But seems to work for Devanagari!
#
# Tried other languages like Malayalam, Telugu and Kannada
# Since they depend on vertical position GPOS engine, they don't
# work. Malayalam works somewhat except for vertical positioning.
#
# This is a messy program that works for Hindi partially, but mostly.
# It implements lookup table type 4 ligature substitutions and type 6
# lookahead and backtrack substitutions partially.
#

from tkinter import *
import sys
import clipboard
import tkinter.font as font
from fontTools.ttLib import TTFont
import xml.etree.ElementTree as ET

# check for available fonts
# if sys.version_info.major == 3:
#    import tkinter as tk, tkinter.font as tk_font
# else:
#    import Tkinter as tk, tkFont as tk_font

finalDisp = ""  # global final display return value
uniDisp = ""  # unicode value display for debugging

# enter the language ttf font below!
# strip and save a temp xml file with only GSUB and cmap tables for the font

font2 = TTFont("akshar.ttf", fontNumber=0)
font2.saveXML("temp.xml", tables=["GSUB", "cmap"])

debug = False
defaultLang1 = False
defaultLang2 = False

# select only one language from below
# English is bypassed and so will also come
# do not select two or more, it won't work correctly!
# I do not know any of the Devanagari languages, but they
# seem to work mostly, but no guarantees!
#
# A few Hindi words like श्री, दर्द do not work! It is
# better to enter these manually inside Affinity.
# In some fonts, the reph sign appears as a rakaar at the
# bottom, and in other cases, the reph sign appears before.
# I really can't help here, since I do not know these rules.

Tamil = False
Deva = True

# the following Dravidian languages don't work correctly
# as they rely mostly on GPOS engine to position char vertically!
# Malayalam seems to work a bit, except for vertical positioning
# I do not know these languages!
Malay = False
Telu = False
Kann = False

if Tamil:

    # ------------------------------------------------------
    # glyph IDs for pre-position/pre-base chars for Tamil, like in கெ கே கை கொ கோ கௌ
    # This list is for Tamil only!
    # These unicode char lists must be changed for other languages!
    # Please port it for other languages too!
    # Other languages like Hindi or Telugu depend heavily on GPOS rules
    # and may not work correctly in this GSUB based program!

    langID = "tml2"  # latest form of Tamil, skip the archaic form tml2
    langID2 = "taml"  # backup name if the first is not found
    prepChar = ["0xbc6", "0xbc7", "0xbc8"]  # single append preposition chars list கெ கே கை
    prep2Char = ["0xbca", "0xbcb", "0xbcc"]  # double append preposition chars list கொ கோ கௌ
    preapp2Char = ["0xbc6", "0xbc7", "0xbc6"]  # pre-append chars
    post2Char = ["0xbbe", "0xbbe", "0xbd7"]  # post-append chars
    postArch = ["0xbbe"]  # for skipping arch Tamil chars
    prepglyID = [0, 0, 0]  # pre-position glyph ID list initialization
    prep2glyID = [0, 0, 0]  # second pre-position glyph ID list initialization
    preapp2glyID = [0, 0, 0]  # pre-append glyph ID list initialization
    post2glyID = [0, 0, 0]  # post-append glyph ID list initialization
    uniRange = [0x0b80, 0x0bff]  # unicode range for the Tamil language
    # -----------------------------------------------------

if Deva:

    # ------------------------------------------------------
    # glyph IDs for pre-position/pre-base chars for Tamil, like in கெ கே கை கொ கோ கௌ
    # This list is for Deva only!
    # These unicode char lists must be changed for other languages!
    # Please port it for other languages too!
    # Other languages like Hindi or Telugu depend heavily on GPOS rules
    # and may not work correctly in this GSUB based program!

    langID = "dev2"  # latest form of Tamil, skip the archaic form tml2
    langID2 = "deva"  # backup name if the first is not found
    prepChar = ["0x94e", "0x93f"]  # single append preposition chars list கெ கே கை
    prep2Char = []  # double append preposition chars list கொ கோ கௌ
    preapp2Char = []  # pre-append chars
    post2Char = []  # post-append chars
    postArch = []  # for skipping arch Tamil chars
    prepglyID = [0, 0]  # pre-position glyph ID list initialization
    prep2glyID = []  # second pre-position glyph ID list initialization
    preapp2glyID = []  # pre-append glyph ID list initialization
    post2glyID = []  # post-append glyph ID list initialization
    uniRange = [0x0900, 0x097f]  # unicode range for the Tamil language
    # -----------------------------------------------------

if Malay:

    # ------------------------------------------------------
    # glyph IDs for pre-position/pre-base chars for Malayalam, like in கெ கே கை கொ கோ கௌ
    # This list is for Malay only!
    # These unicode char lists must be changed for other languages!
    # Please port it for other languages too!
    # Other languages like Hindi or Telugu depend heavily on GPOS rules
    # and may not work correctly in this GSUB based program!

    langID = "mlm2"  # latest form of Tamil, skip the archaic form tml2
    langID2 = "mlym"  # backup name if the first is not found
    prepChar = ["0xd46", "0xd47", "0xd48"]  # single append preposition chars list கெ கே கை
    prep2Char = ["0xd4a", "0xd4b", "0xd4c"]  # double append preposition chars list கொ கோ கௌ
    preapp2Char = ["0xd46", "0xd47", "0xd46"]  # pre-append chars
    post2Char = ["0xd3e", "0xd3e", "0xd57"]  # post-append chars
    prepglyID = [0, 0, 0]  # pre-position glyph ID list initialization
    prep2glyID = [0, 0, 0]  # second pre-position glyph ID list initialization
    preapp2glyID = [0, 0, 0]  # pre-append glyph ID list initialization
    post2glyID = [0, 0, 0]  # post-append glyph ID list initialization
    uniRange = [0x0d00, 0x0d7f]  # unicode range for the Malayalam language
    # -----------------------------------------------------

if Telu:

    # ------------------------------------------------------
    # glyph IDs for pre-position/pre-base chars for Telugu, like in கெ கே கை கொ கோ கௌ
    # This list is for Telugu only!
    # These unicode char lists must be changed for other languages!
    # Please port it for other languages too!
    # Other languages like Hindi or Telugu depend heavily on GPOS rules
    # and may not work correctly in this GSUB based program!

    langID = "tel2"  # latest form of Tamil, skip the archaic form tml2
    langID2 = "telu"  # backup name if the first is not found
    prepChar = []  # single append preposition chars list கெ கே கை
    prep2Char = []  # double append preposition chars list கொ கோ கௌ
    preapp2Char = []  # pre-append chars
    post2Char = []  # post-append chars
    prepglyID = []  # pre-position glyph ID list initialization
    prep2glyID = []  # second pre-position glyph ID list initialization
    preapp2glyID = []  # pre-append glyph ID list initialization
    post2glyID = []  # post-append glyph ID list initialization
    uniRange = [0x0c00, 0x0c7f]  # unicode range for the Malayalam language
    # -----------------------------------------------------

if Kann:

    # ------------------------------------------------------
    # glyph IDs for pre-position/pre-base chars for Kannada, like in கெ கே கை கொ கோ கௌ
    # This list is for Telugu only!
    # These unicode char lists must be changed for other languages!
    # Please port it for other languages too!
    # Other languages like Hindi or Telugu depend heavily on GPOS rules
    # and may not work correctly in this GSUB based program!

    langID = "knd2"  # latest form of Tamil, skip the archaic form tml2
    langID2 = "knda"  # backup name if the first is not found
    prepChar = []  # single append preposition chars list கெ கே கை
    prep2Char = []  # double append preposition chars list கொ கோ கௌ
    preapp2Char = []  # pre-append chars
    post2Char = []  # post-append chars
    prepglyID = []  # pre-position glyph ID list initialization
    prep2glyID = []  # second pre-position glyph ID list initialization
    preapp2glyID = []  # pre-append glyph ID list initialization
    post2glyID = []  # post-append glyph ID list initialization
    uniRange = [0x0c80, 0x0cff]  # unicode range for the Malayalam language
    # -----------------------------------------------------

print(font2.keys())

# check if GSUB is found
GSUBfound = False
for c in font2.keys():
    if c == 'GSUB':
        print ("GSUB found in the entered font file")
        GSUBfound = True

if not GSUBfound:
    print("GSUB not found in font file, quitting!")
    quit()

# parse xml tree
tree = ET.parse('temp.xml')

# getting the parent tag of
# the xml document
root = tree.getroot()

# read other link and subst data from the xml font file
substList = []  # final type 4 substitution data
subst1List = []  # final type 1 substitution data
subst1BTList = []  # final type 1 substitution data
subst6List = []  # final type 6 LA substitution data
subst6BTList = []  # final type 6 BT substitution data

# first get feature list
featlist = []  # list of features in GSUB
for c in root.iter('ScriptRecord'):
    scriptrecord = c.get("index")
    for d in c.iter('ScriptTag'):
        scripttag = d.get("value")
        for e in c.iter('FeatureIndex'):
            featindex = e.get("index")
            featvalue = e.get("value")
            featlist.append([scriptrecord, scripttag, featindex, featvalue])
#print(featlist)

lookuplist = []  # list of lookup indices
for c in root.iter('FeatureRecord'):
    featurerecordindex = c.get("index")
    for d in c.iter('FeatureTag'):
        featuretag = d.get("value")
        for e in c.iter('LookupListIndex'):
            lookuplistindex = e.get("index")
            lookuplistval = e.get("value")
            lookuplist.append([featurerecordindex, featuretag, lookuplistindex, lookuplistval])
#print(lookuplist)

# check which version of tml2 or taml is present
# search whole list first
for j in range(0, len(featlist)):
    if langID == featlist[j][1]:  # check first if tml2 is found
        defaultLang1 = True
    if langID2 == featlist[j][1]:  # check next if taml is found
        defaultLang2 = True

# print(defaultLang1, defaultLang2)

lkList = []  # linked list
if defaultLang1:
    # print("got to 1st language")
    for j in range(0, len(featlist)):
        if langID == featlist[j][1]:  # check first if tml2 is found
            lkList.append(featlist[j][3])
            print("default language found =", langID)
    # else:
    #     print('selected font file has other languages! =', featlist[j][1])
    #     #quit()

elif defaultLang2:
    # print("got to 2nd language")
    for j in range(0, len(featlist)):
        if langID2 == featlist[j][1]:  # check if the other archaic form taml is found
                lkList.append(featlist[j][3])
                print("language found is old", langID2)

print("Feature table index: lkList =", lkList)

# now get link list of lookup tables to use in correct order
llList = []
for k in range(0, len(lkList)):
    for j in range(0, len(lookuplist)):
        if (lookuplist[j][0]) == lkList[k]:
            llList.append(lookuplist[j][3])
            continue
print("Lookup table index: llList =", llList)

# get char substitution type 4 list here, easier to work with glyph ID, so get glyph ID
j = 0

for k in range(0, len(llList)):
    for c in root.iter('Lookup'):
        subsetindex = c.get('index')
        if llList[k] == subsetindex:  # check in right order
            for d in c.iter('LigatureSet'):  # effectively search on for type 4 subst
                forglyph = (d.get('glyph'))  # for this glyph, with glyph ID
                for e in d.iter('Ligature'):
                    substcomp = str(e.get('components')).split(",")  # next component, split if more than 1
                    for k in range(0, len(substcomp)):
                        substcomp[k] = (substcomp[k])
                    substglyph = (e.get('glyph'))
                    substList.append([(forglyph),
                                      (substcomp),(substglyph)])
                    # if debug:
                    #     if (forglyph == 'uni0940'):  # for debugging a particular char
                    #         print("forglyph name= ", [(forglyph),
                    #                       (substcomp),(substglyph)])

                    j = j + 1
            continue  # get substitute list in correct order

print("number of substitutions type 4 to be made =", j)

if debug:
    print(substList)

# get char substitution type 6 LA list here, easier to work with glyph ID, so get glyph ID
j = 0

for k in range(0, len(llList)):
    for c in root.iter('Lookup'):
        subset6index = c.get('index')
        if llList[k] == subset6index:  # check in right order
            temp1 = []
            for d in c.iter('InputCoverage'):  # effectively search on for type 4 subst
                index1 = d.get('index')
            for d in c.iter('SubstLookupRecord'):
                index2 = d.get('index')
            for d in c.iter('LookAheadCoverage'):
                index3 = d.get('index')

            for d in c.iter('InputCoverage'):  # effectively search on for type 4 subst
                for e in d.iter('Glyph'):  # effectively search on for type 4 subst
                    inputglyph = (e.get('value'))  # for in glyph
                    temp1.append(inputglyph)

            temp2 = ""
            for d in c.iter('SubstLookupRecord'):
                for e in d.iter('LookupListIndex'):
                    looklistindex = (e.get('value'))
                    temp2 = temp2+ looklistindex

            temp3 = []
            for d in c.iter('LookAheadCoverage'):
                for e in d.iter('Glyph'):
                    lookaheadglyph = (e.get('value'))
                    temp3.append(lookaheadglyph)

                subst6List.append([index1, index3, index2, temp1, temp3,temp2])
                #print([temp1, temp3, temp2])
                j = j + 1


           # if debug:
            #         if (inputglyph == 'uni093F'):  # for debugging a particular char
            #             print("inglyph name= ", [inputglyph, temp, looklistindex])

            continue  # get substitute list in correct order

print("number of LA substitutions type 6 to be made =", j)
#print((subst6List))

if debug:
    print(subst6List)

# get char substitution type 6 BT list here, easier to work with glyph ID, so get glyph ID
j = 0

for k in range(0, len(llList)):
    for c in root.iter('Lookup'):
        subset6BTindex = c.get('index')
        if llList[k] == subset6BTindex:  # check in right order
            tempBT1 = []
            for d in c.iter('InputCoverage'):  # effectively search on for type 4 subst
                indexBT1 = d.get('index')
            for d in c.iter('SubstLookupRecord'):
                indexBT2 = d.get('index')
            for d in c.iter('BacktrackCoverage'):
                indexBT3 = d.get('index')

            for d in c.iter('InputCoverage'):
                for e in d.iter('Glyph'):  # effectively search on for type 4 subst
                    inputglyph = (e.get('value'))  # for in glyph
                    tempBT1.append(inputglyph)

            tempBT2 = ""
            for d in c.iter('SubstLookupRecord'):
                for e in d.iter('LookupListIndex'):
                    looklistBTindex = (e.get('value'))
                    tempBT2 = tempBT2 + (looklistBTindex)

            tempBT3 = []
            for d in c.iter('BacktrackCoverage'):
                for e in d.iter('Glyph'):
                    backtrackglyph = (e.get('value'))
                    tempBT3.append(backtrackglyph)

                subst6BTList.append([indexBT1, indexBT3, indexBT2, tempBT1, tempBT3, tempBT2])
                j = j + 1

            # if debug:
            #         if (inputglyph == 'uni093F'):  # for debugging a particular char
            #             print("inglyph name= ", [inputglyph, temp, looklistindex])
            #     #

            continue  # get substitute list in correct order

print("number of BT substitutions type 6 to be made =", j)
#print((subst6BTList))

if debug:
    print(subst6BTList)


# get char substitution LA type 1 list here, easier to work with glyph ID, so get glyph ID
j = 0

for k in range(0, len(subst6List)):
    for c in root.iter('Lookup'):
        subset6index = c.get('index')
        if subst6List[k][5] == subset6index:  # check in right order
            for d in c.iter('Substitution'):  # effectively search on for type 4 subst
                inglyph = (d.get('in'))  # for in glyph
                outglyph = (d.get('out'))  # for in glyph
                subst1List.append([subset6index, inglyph, outglyph])
                j = j + 1
                if debug:
                    if (inglyph == 'uni0940'):  # for debugging a particular char
                        print("inglyph name= ", [inglyph, outglyph])

            continue  # get substitute list in correct order

print("number of LA substitutions type 1 to be made =", j)
#print(subst1List)

if debug:
    print(subst1List)

# get char substitution BT type 1 list here, easier to work with glyph ID, so get glyph ID
j = 0

for k in range(0, len(subst6BTList)):
    for c in root.iter('Lookup'):
        subset6BTindex = c.get('index')
        if subst6BTList[k][5] == subset6BTindex:  # check in right order
            for d in c.iter('Substitution'):  # effectively search on for type 4 subst
                inglyph = (d.get('in'))  # for in glyph
                outglyph = (d.get('out'))  # for in glyph
                subst1BTList.append([subset6BTindex, inglyph, outglyph])
                j = j + 1
                if debug:
                    if (inglyph == 'uni0940'):  # for debugging a particular char
                        print("inglyph name= ", [inglyph, outglyph])

            continue  # get substitute list in correct order

print("number of BT substitutions type 1 to be made =", j)
#print(subst1BTList)

if debug:
    print(subst1BTList)

k = 0
cmapList = []
# get mapped glyph names for unicode codes from cmap data
for Map in root.iter('map'):
    mapCode = str(Map.get('code'))
    glyphName = str(Map.get('name'))
    cmapList.append([mapCode, glyphName])
    k = k + 1
print("total number of all glyphs in cmap=", k)
#print(cmapList)

# find names for CR and LF names in cmap
for k in range(0, len(cmapList)):
    if cmapList[k][0] == '0xa':
        CRName = cmapList[k][1]
    if cmapList[k][0] == '0xd':
        LFName = cmapList[k][1]
    if cmapList[k][0] == '0x20':
        SpaceName = cmapList[k][1]
    if cmapList[k][0] == '0x200c':
        ZWNJName = cmapList[k][1]
    if cmapList[k][0] == '0x200d':
        ZWJName = cmapList[k][1]

#print("CR, LF names =", CRName, LFName)

# initialize some variables
l = 0
ll = 0

# assume that they must be in the unicode fonts!
for l in range(0, len(prepChar)):
    for ll in range(0, len(cmapList)):
        if prepChar[l] == cmapList[ll][0]:
            prepglyID[l] = font2.getGlyphID(cmapList[ll][1])
            continue

if debug:
    print("pre-position one char glyph IDs = ", prepglyID)  # like கெ கே கை

# assume that they must be in the unicode fonts!
for l in range(0, len(prep2Char)):
    for ll in range(0, len(cmapList)):
        if prep2Char[l] == cmapList[ll][0]:
            prep2glyID[l] = font2.getGlyphID(cmapList[ll][1])
            continue

if debug:
    print("pre-position two char glyph IDs = ", prep2glyID)  # கொ கோ கௌ

# assume that they must be in the unicode fonts!
for l in range(0, len(preapp2Char)):
    for ll in range(0, len(cmapList)):
        if preapp2Char[l] == cmapList[ll][0]:
            preapp2glyID[l] = font2.getGlyphID(cmapList[ll][1])
            continue

if debug:
    print("pre-append two char glyph IDs = ", preapp2glyID)  # like the first glyph in after கௌ

# assume that they must be in the unicode fonts!
for l in range(0, len(post2Char)):
    for ll in range(0, len(cmapList)):
        if post2Char[l] == cmapList[ll][0]:
            post2glyID[l] = font2.getGlyphID(cmapList[ll][1])
            continue

if debug:
    print("post-append char glyph IDs = ", post2glyID)  # like the third ள after கௌ


# open Tk window
root = Tk()
root.title('A simple Unicode to opentype glyph format converter for Affinity programs')

# create Font in default display screen object
myFont = font.Font(family='Helvetica')

# copy some sample text into clipboard for testing the program
#clipboard.copy("test chars \n mathi தமிழ் மொழி Mathiazhagan \n லக்‌ஷமி லக்‌ஷ்மி ஶ்ரீ ஸ்ரீ கை சித்து தூ பு பூ மெ க்‌ஷ் மொ கை வெ றா சிந்து")
clipboard.copy("अक्षय, राजा, रूपी, श्री , र्जी , दर्द  \n, mathi, test")
#clipboard.copy("श्री, र्जी, दर्द")

clipText = clipboard.paste()  # text will have the content of clipboard
# sanskrit characters like ஶ்ரீ or க்‌ஷ need level 3 substitution not implemented here.

# print available fonts
# print(tk_font.families())
# print(tk_font.names())


def clear_all():
    global finalDisp
    global clipText
    finalDisp = ""
    clipboard.copy(finalDisp)  # now the clipboard content will be cleared
    clipText = clipboard.paste()  # text will have the content of clipboard
    textBox.delete("1.0", END)  # clear text boxes
    textBox2.delete("1.0", END)
    textBox3.delete("1.0", END)
    print('screen and clipboard cleared')


def copy_clipboard():  # copy glyph string in third window
    global finalDisp
    global clipText
    clipboard.copy(finalDisp)  # now the clipboard will have the data from third window
    clipText = clipboard.paste()  # text will have the content of clipboard
    print('copy to clipboard done')


# the main routine to read copied data in the first window, do all the substitutions,
# and display the final converted file in the third window! The second windows shows
# unicode values of the input chars, useful for debugging.
def retrieve_input():

    global finalDisp  # global so can be used in routines
    global uniDisp  # display unicode value in 2nd window for debugging

    finalDisp = ""  # initialize final display string in third window!
    uniDisp = ""  # initialize unicode display string 2nd window!

    #   manipulate the unicode string and convert
    inputValue = textBox.get("1.0", "end-1c")
    #inputValue = inputValue  # pad extra 3 space for level 3

    charAppend = ""  # char append variable in third window
    uniAppend = ""  # unicode char append variable in 2nd window for debug

    startpos = 0
    word = ""

    for ijk in range(startpos, len(inputValue)):  # for display unicode values in second window

        uniDisp = uniDisp + uniAppend  # for displaying unicode string 2nd window
        word = ""

        uniAppend = hex(ord(inputValue[ijk]))+","
        if ord(inputValue[ijk]) < 31:
            uniAppend = "\n"
            #charAppend = "\n"
            continue

        #read one word at a time by looking for space or CR

        for ii in range(startpos, len(inputValue)):
            word = word + (inputValue[ii])
            startpos = ii+1
            if ord(inputValue[ii]) == 32:  # include space and below for word end!
                break  # break the above ii loop and continue

            # if ord(inputValue[ii]) < 32:  # include space and below for word end!
            #     word = word + "\r"
            #     continue  # break the above ii loop and continue

        # ignore empty spaces at the end of textbox
        if word == "":
            continue

        if debug:
            print("ijk, word =", ijk, word)

        wordname = [None]*(len(word)+2)  # pad 1 extra space
        # convert word to nameList
        for i in range(0, len(cmapList)):
            for i2 in range(0, len(word)):
                # assume all these are CR returns
                if ord(word[i2]) == 0x0a :
                    wordname[i2] = 'LFName'
                elif ord(word[i2]) == 0x0d :
                    wordname[i2] = 'CRName'
                elif ord(word[i2]) == 0x20:
                    wordname[i2] = 'SpaceName'
                elif ord(word[i2]) == 0x2008:
                    wordname[i2] = 'SpaceName'
                elif ord(word[i2]) == 0x2009:
                    wordname[i2] = 'SpaceName'
                elif ord(word[i2]) == 0x2028 :  # line break actually
                    wordname[i2] = 'LineBreak'
                elif ord(word[i2]) == 0x2029 :  # para separator
                    wordname[i2] = 'ParaSeparator'
                elif hex(ord(word[i2])) == cmapList[i][0]:
                    wordname[i2] = (cmapList[i][1])
                    continue

        if debug:
            print("ijk, wordname =", ijk, wordname)

        replace = 0
        nextpos = 0
        wordnamelen = len(wordname)

        # swap first
        for j2 in range(0, len(wordname) - 1):  # skip last one!
            # now do swapping, if done all substitutions
            for i4 in range(0, len(prepglyID)):
                if wordname[j2 + 1] == font2.getGlyphName(prepglyID[i4]):
                    tempvalue = wordname[j2]
                    wordname[j2] = wordname[j2 + 1]
                    wordname[j2 + 1] = tempvalue
                    continue

        for j2 in range(0, len(wordname) - 1):
            # now do swapping, if done all substitutions
            for i4 in range(0, len(prep2glyID)):
                if wordname[j2 + 1] == font2.getGlyphName(prep2glyID[i4]):
                    if j2 - 1 < 0:  # if in 0th place insert there, otherwise normal
                        wordname.insert(0, font2.getGlyphName(preapp2glyID[i4]))
                    else:
                        wordname.insert(j2, font2.getGlyphName(preapp2glyID[i4]))
                    wordname[j2 + 2] = font2.getGlyphName(post2glyID[i4])
                    continue
        if debug:
            print("after all swapping done", wordname)

        for ij in range(0, wordnamelen):
            nextpos = 0
            replace = 0
            charpos = 0
            substdone = False
            for i2 in range(nextpos, wordnamelen):
                charpos = i2 - replace  # current char pos in word

                # LA substitution
                for i3 in range(0, len(subst6List)):
                    # print("subst6 ", wordname[charpos], subst6List[i3][0][0])
                    for i4 in range(0, len(subst6List[i3][3])):
                        if wordname[charpos] == subst6List[i3][3][i4]:
                            # print("before subst6 ", len(subst6List[i3][4]), wordname[charpos], subst6List[i3][3][0])
                            if subst6List[i3][0] == '0' and subst6List[i3][1] == '0':
                                #print("before subst6 ", len(subst6List[i3][4]), wordname[charpos], subst6List[i3][3][0])
                                for j3 in range(0, len(subst6List[i3][4])):
                                    if wordname[charpos + 1] == subst6List[i3][4][j3]:
                                        if debug:
                                            print("after subst6 0 0 ", (subst6List[i3][4][j3]), wordname[charpos + 1],
                                                  subst6List[i3][5])
                                        for k3 in range(0, len(subst1List)):
                                            if subst6List[i3][5] == subst1List[k3][0]:
                                                if debug:
                                                    print("final before LA 0 0", wordname[charpos], subst1List[k3][0],
                                                          subst1List[k3][2])
                                                wordname[charpos] = subst1List[k3][2]
                                                if debug:
                                                    print("final after LA 0 0", wordname[charpos], subst1List[k3][0],
                                                          subst1List[k3][2])
                                                    print("final LA 0 0", word, wordname)

                                                substdone = True
                                                continue

                            if subst6List[i3][0] == '1' and subst6List[i3][1] == '0':
                                # print("2 seq. before subst6 ", len(subst6List[i3][4]), wordname[charpos],
                                #       subst6List[i3][3][0])
                                if wordname[charpos + 1] == subst6List[i3][3][1]:  # two chars seq.
                                    # print("2 seq. before subst6 ", len(subst6List[i3][4]), wordname[charpos],
                                    #       subst6List[i3][3][0])
                                    for j3 in range(0, len(subst6List[i3][4])):
                                        if wordname[charpos + 2] == subst6List[i3][4][j3]:
                                            if debug:
                                                print("after subst6 1 0 ", (subst6List[i3][4][j3]),
                                                       wordname[charpos + 1], subst6List[i3][5])
                                            for k3 in range(0, len(subst1List)):
                                                if subst6List[i3][5] == subst1List[k3][0]:
                                                    if debug:
                                                        print("final LA 1 0 before", wordname[charpos], subst1List[k3][0],
                                                              subst1List[k3][2])
                                                    wordname[charpos] = subst1List[k3][2]
                                                    if debug:
                                                        print("final LA 1 0 after", wordname[charpos], subst1List[k3][0],
                                                              subst1List[k3][2])
                                                        print("final LA 1 0", word, wordname)

                                                    substdone = True
                                                    continue

                # BT substitution
                for i3 in range(0, len(subst6BTList)):
                    # print("subst6 ", wordname[charpos], subst6List[i3][0][0])
                    for i4 in range(0, len(subst6BTList[i3][3])):
                        if wordname[charpos] == subst6BTList[i3][3][i4]:
                            # print("before subst6 ", len(subst6List[i3][4]), wordname[charpos], subst6List[i3][3][0])
                            if subst6BTList[i3][0] == '0' and subst6BTList[i3][1] == '0':
                                # print("before subst6 ", len(subst6List[i3][4]), wordname[charpos], subst6List[i3][3][0])
                                for j3 in range(0, len(subst6BTList[i3][4])):
                                    if wordname[charpos - 1] == subst6BTList[i3][4][j3]:
                                        if debug:
                                            print("after subst6BT 0 0 ", (subst6BTList[i3][4][j3]),
                                                  wordname[charpos - 1], subst6BTList[i3][5])
                                        for k3 in range(0, len(subst1BTList)):
                                            if subst6BTList[i3][5] == subst1BTList[k3][0]:
                                                if debug:
                                                    print("final BT  0 0 before", wordname[charpos], subst1BTList[k3][0],
                                                          subst1BTList[k3][2])
                                                wordname[charpos] = subst1BTList[k3][2]
                                                if debug:
                                                    print("final BT 0 0 after", wordname[charpos], subst1BTList[k3][0],
                                                          subst1BTList[k3][2])
                                                    print("final BT 0 0", word, wordname)

                                                substdone = True
                                                continue

                            if subst6BTList[i3][0] == '1' and subst6BTList[i3][1] == '0':
                                # print("2 seq. before subst6BT ", len(subst6BTList[i3][4]), wordname[charpos],
                                #       subst6BTList[i3][3][0])
                                if wordname[charpos - 1] == subst6BTList[i3][3][1]:  # two chars seq.
                                    # print("2 seq. before subst6BT ", len(subst6BTList[i3][4]),
                                    #       wordname[charpos], subst6BTList[i3][3][0])
                                    for j3 in range(0, len(subst6BTList[i3][4])):
                                        if wordname[charpos - 2] == subst6BTList[i3][4][j3]:
                                            if debug:
                                                print("after subst6 1 0 ", (subst6BTList[i3][4][j3]),
                                                      wordname[charpos - 2], subst6BTList[i3][5])
                                            for k3 in range(0, len(subst1BTList)):
                                                if subst6BTList[i3][5] == subst1BTList[k3][0]:
                                                    if debug:
                                                        print("final BT 1 0 before", wordname[charpos],
                                                              subst1BTList[k3][0], subst1BTList[k3][2])
                                                    wordname[charpos] = subst1BTList[k3][2]
                                                    if debug:
                                                        print("final BT 1 0 after", wordname[charpos],
                                                              subst1BTList[k3][0], subst1BTList[k3][2])
                                                        print("final BT 1 0", word, wordname)

                                                    substdone = True
                                                    continue

                # type 4 subst 3, 2 and 1 components
                for i3 in range(0, len(substList)):
                    if wordname[charpos] == substList[i3][0]:  #current char is in subst list
                        substword = wordname[charpos]
                        substComponent = substList[i3][1]
                        substValue = substList[i3][2]

                        if len(substComponent) == 3:  # first do double length subst
                            if wordname[charpos + 1] == ZWNJName:
                                if (substComponent[0] == wordname[charpos + 1]) and (
                                        substComponent[2] == wordname[charpos + 3]):
                                    #print("got to level 3 with zwj")
                                    wordname[charpos] = substValue
                                    del wordname[charpos + 1]  # delete that replaced char
                                    del wordname[charpos + 1]
                                    del wordname[charpos + 1]
                                    wordnamelen = wordnamelen - 3
                                    nextpos = charpos+1;  # we deleted one char, so nextpos is same
                                    replace = replace + 3
                                    substdone = True
                                    if debug:
                                        print("aft L3zwnj ij, charpos, nextpos, rep, len, new wordname", ij, charpos, nextpos,
                                              replace, wordnamelen, word[charpos],
                                              word[charpos + 1], word[charpos + 2], substword, substComponent, substValue)
                                    break  # break i3 loop

                            else:  # if no ZWNJ, do these
                                 if (substComponent[0] == wordname[charpos+1]) and (substComponent[1]
                                    == wordname[charpos+2]) and (substComponent[2] == wordname[charpos+3]):
                                    #print("got to level 3")
                                    wordname[charpos] = substValue
                                    del wordname[charpos+1]  # delete that replaced char
                                    del wordname[charpos+1]
                                    del wordname[charpos+1]
                                    wordnamelen = wordnamelen -3
                                    nextpos = charpos + 1;  # we deleted one char, so nextpos is +1
                                    replace = replace + 3
                                    substdone = True
                                    if debug:
                                        print("aft L3 ij, charpos, nextpos, rep, len, new wordname", ij, charpos, nextpos, replace, wordnamelen, word[charpos],
                                              word[charpos + 1], word[charpos+2], substword, substComponent, substValue)
                                    break  # break i3 loop

                        elif len(substComponent) == 2:  # first do double length subst
                            if (substComponent[0] == wordname[charpos + 1]) and (
                                    substComponent[1] == wordname[charpos + 2]):
                                #print("got to level 2")
                                wordname[charpos] = substValue
                                del wordname[charpos + 1]  # delete that replaced char
                                del wordname[charpos + 1]
                                wordnamelen = wordnamelen - 2
                                nextpos = charpos + 1;  # we deleted two char, so nextpos is +1
                                replace = replace + 2
                                substdone = True
                                if debug:
                                    print("aft L2 ij, charpos, nextpos, rep, len, new wordname", ij, charpos, nextpos,
                                          replace, wordnamelen, word[charpos],
                                          word[charpos + 1], word[charpos + 2], substword, substComponent, substValue)
                                break  # break i3 loop

                        elif len(substComponent) == 1:  # first do single length subst
                             if substComponent[0] == wordname[charpos+1]:
                                #print("got to level 1")
                                wordname[charpos] = substValue
                                del wordname[charpos + 1]  # delete that replaced char
                                wordnamelen = wordnamelen -1
                                nextpos = charpos + 1;  # we deleted one char, so nextpos is same
                                replace = replace + 1
                                substdone = True
                                if debug:
                                    print("aft L1 ij, charpos, nextpos, rep, len, new wordname", ij, charpos, nextpos, replace, wordnamelen, word[charpos],
                                           word[charpos + 1], substword, substComponent, substValue)
                                break   # break i3 loop

            if debug:
                print("iter no. ij, no. of substs., final wordname =", ij, replace, wordname)
            # if (charpos+replace) > wordnamelen-1:  # recheck logic here!
            #     break

            if not substdone:
                   break  # break ij loop if no more subst required


        for j3 in range(0, len(wordname)):
            # now do char append
            if wordname[j3] == None:
                charAppend = ""
                #continue
            elif wordname[j3] == 'LFName':
                charAppend = "\n"
            elif wordname[j3] == 'CRName':
                charAppend = "\r"
            elif wordname[j3] == 'ZWNJName':
                charAppend = ""
            elif wordname[j3] == 'ZWJName':
                charAppend = ""
            elif wordname[j3] == 'SpaceName':
                charAppend = " "
            elif wordname[j3] == 'LineBreak':
                charAppend = "u+2028"
            elif wordname[j3] == 'ParaSeparator':
                charAppend = "u+2029"
            else:
                wordID = (font2.getGlyphID(wordname[j3]))
                charAppend = "g+" + (hex(wordID)).replace("0x", "")

            finalDisp = finalDisp + charAppend
    #quit()
    #print(finalDisp)
    print('conversion done')

    textBox3.insert(INSERT, uniDisp)
    textBox2.insert(INSERT, finalDisp)

# display first text box using std font
textBox = Text(root, height=10, width=100, font=myFont)
textBox.pack(pady=10)

# display second text box using target font
textBox3 = Text(root, height=5, width=100, font=myFont)
textBox3.pack(pady=10)

# display third text box with unicode values using target font for debugging
textBox2 = Text(root, height=5, width=100, font=myFont)
textBox2.pack(pady=10)

# button clicks section
buttonCommit = Button(root, height=1, width=10, text="Convert", font=myFont,
                      command=lambda: retrieve_input())
# command=lambda: retrieve_input() >>> just means do this when i press the button
buttonCommit.pack()

buttonCommit2 = Button(root, height=1, width=10, text="Copy", font=myFont,
                       command=lambda: copy_clipboard())
# command=lambda: retrieve_input() >>> just means do this when i press the button
buttonCommit2.pack()

buttonCommit3 = Button(root, height=1, width=10, text="Clear", font=myFont,
                       command=lambda: clear_all())
# command=lambda: retrieve_input() >>> just means do this when i press the button
buttonCommit3.pack()

mainloop()




