#!/usr/bin/python3
import datetime
import os
import exifread
# import exiv2
import platform

def creation_date(path_to_file):
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            return stat.st_mtime


def modified_date(path_to_file):
    stat = os.stat(path_to_file)
    return stat.st_mtime


dir1 = '.'


files1 = []
fullpaths1 = []

for dirname, dirnames, filenames in os.walk(dir1):
    for subdirname in dirnames:
        fullpath = os.path.join(dirname, subdirname)
        if (fullpath.find("resources") < 0):
            print(fullpath)

    for filename in filenames:
        fullpath=os.path.join(dirname, filename)
        if (fullpath.find("resources") < 0):
            fullpaths1 += [fullpath]

no_exif_data_filename = dir1+"/no_exif_data.txt"
no_exif_data_file = open(no_exif_data_filename, "w")
no_exif_data_file.write("These photos don't have any EXIF data\n")

output_filename = dir1+"/touchAllImages.sh"
output_file = open(output_filename, 'w')
output_file.write("echo Tohuching all the EXIFs on files starting from path: '"+dir1+"'\n")
for file1 in fullpaths1:
    if (str(file1).upper().endswith('JPG')) or (str(file1).upper().endswith('JPEG')) or (str(file1).upper().endswith('CR2')) or (str(file1).upper().endswith('PNG')) or (str(file1).upper().endswith('GIF')) or (str(file1).upper().endswith('HEIC')):
        f = open(file1, 'rb')
        try:
            tags = exifread.process_file(f) # use only this line if you're importing exifread
            # image = exiv2.ImageFactory.open(file1)
            # image.readMetadata()
            # tags = image.exifData()
            # print(file1)
            # tags['Exif.Image.DateTimeOriginal']._print()
        except Exception as e:
            f.close()
            print(e)
            continue
        f.close()
        subsec="00"
        found_date_tag = False
        found_backup_date_tag = False
        if tags:
            print('=============================================================================================================')
            #print(file1)
            file1_modified_date = str(int(modified_date(file1)))
            escaped_filename = ''
            for c in file1:
                if (c == ' ') | (c == '&') | (c == '(') | (c == ')') | (c == '[') | (c == ']') | (c == "'"):
                    escaped_filename += '\\'
                escaped_filename += c
            try:
                for tag in tags.keys():
                    if str(tag).upper().find("SUBSECTIME") > 0:
                        subsec = str(tags[tag])
                    if tag == 'EXIF DateTimeOriginal':
                        found_date_tag = True
                        primary_date_tag = tag
                        break
                    else:
                        if (str(tag).upper().find("DATETIME") > 0):
                            # print('Found a date time tag other than "EXIF DateTimeOriginal": ' + str(tag) + ": " + str(tags[tag]))
                            found_backup_date_tag = True
                            backup_date_tag = tag

                for tag in tags.keys():
                    if found_date_tag:
                        tag = primary_date_tag
                        print('Using tag: ' + tag)
                        EXIFDateTimeOriginal = str(tags[tag]) + '.' + subsec
                        touchDateTime = EXIFDateTimeOriginal[0:4]+ \
                                        EXIFDateTimeOriginal[5:7] + \
                                        EXIFDateTimeOriginal[8:10] + \
                                        EXIFDateTimeOriginal[11:13] + \
                                        EXIFDateTimeOriginal[14:16] + \
                                        '.'+EXIFDateTimeOriginal[17:19]

                        #       touch [-A [-][[hh]mm]SS] [-acfhm] [-r file] [-t [[CC]YY]MMDDhhmm[.SS]] file ...
                        #       touch -c -t 201405112145.28 ./Photos/IMG_1389.JPG

                        creation_datetime = datetime.datetime.strptime(str(tags[tag]), '%Y:%m:%d %H:%M:%S').strftime("%s")
                        if abs(int(file1_modified_date) - int(creation_datetime)) == 0:
                            print(escaped_filename + " file modified date: " + file1_modified_date + " and EXIF Creation Date: " + creation_datetime + " match")
                            break
                        print(escaped_filename + " file creation date: " + file1_modified_date + " and EXIF Creation Date: " + creation_datetime + " don't match")
                        print("DATE: '%s'\ntouch -c -t '%s' %s" % (EXIFDateTimeOriginal, touchDateTime, escaped_filename))
                        commandLine = "touch -c -t "+touchDateTime+" "+escaped_filename+"\n"

                        #<This block is for creating zero bytes files with the timestamp in the front part of the name and the filename at the end, adding .DAT extension>
                        #imagename = escaped_filename[escaped_filename.rfind("/")+1:]
                        #imagepath = escaped_filename[0:escaped_filename.rfind("/")+1]
                        #print(imagename)
                        #print(imagepath)
                        #commandLine = "touch " + imagepath + touchDateTime + "__" + imagename + ".DAT\n"
                        #print(commandLine)
                        #continue #only print, don't create the file
                        #</This block is for creating zero bytes files with the timestamp in the front part of the name and the filename at the end, adding .DAT extension>

                        try:
                            if float(touchDateTime) == 0.0:
                                print("ZERO DATE for '" + escaped_filename + "'")
                                commandLine = "echo '"+escaped_filename+"' ERROR: date is zero\n"
                        except:
                            print("INVALID DATE for '" + escaped_filename + "'")
                            commandLine = "echo '" + escaped_filename + "' ERROR: date is invalid\n"
                        output_file.write(commandLine)
                        break



            except Exception as e:
                print("Exeption '" + str(e) + "' for '" + escaped_filename + "'" + " creation_datetime='" + creation_datetime + "'")
                commandLine = "echo '" + escaped_filename + "' ERROR: EXIF is invalid\n"
                output_file.write(commandLine)
                continue
        else:
            print('=============================================================================================================')
            print("NO EXIF DATA FOR: " + str(file1))
            no_exif_data_file.write("NO EXIF DATA FOR: " + str(file1) + "\n")
output_file.close()
no_exif_data_file.close()
os.system("chmod +x " + output_filename)

