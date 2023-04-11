# set_file_date_to_exif_creation_date
It compares the file creation dates of JPG/JPEG, CR2 (Canon RAW files), PNG, GIF and HEIC files on the current directory and below, against the creation dates stored internally on each file, in their EXIF metadata.
If the two dates are different, then it creates a bash script named "touch_all_images.sh", which sets the file dates of these files to the ones in the EXIF data.
It's safe to run, as it won't change any dates of any of the photos.
In order to do that change, you'll have to run the "touch_all_images.sh" generated script afterwards.
