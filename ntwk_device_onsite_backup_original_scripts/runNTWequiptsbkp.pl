#!/usr/bin/perl
#

use 5.010; #for taking the filesize

#define variables
$HOME = "/home/edna_support/BACKUPS_NTWK"; #home of script
$TIMESTAMP = `date`; #get the localdate
$HOW_OLD = "-6 minute"; #files older than this time are taken
$PATTERN = "*-backup-*"; #find pattern
$BKP_DIR_PATTERN = "network_device_backup*"; #find pattern
$FILES_DIR = "$HOME/backups/"; #where files are stored
$ONSITE_BKP_DIR = "$HOME/backups/"; #where backup is stored
$BACKUP_SCRIPT = "$HOME/bin/getSWconfiguration.expect"; #expect script to be called

#remote part
$OMBS_SERVER = "10.1.90.10";
$OMBS_USERNAME = "ntwkbkup";
$OMBS_DIR = "/data1/network_dev_backups/";


#get the number of hosts from expect script
$nr_hosts = `cat $HOME/bin/getSWconfiguration.expect  | grep dict | grep password | awk '{print \$4}' | tail -1`;

#some trimming
chomp($nr_hosts);
chomp($TIMESTAMP);

print "$TIMESTAMP: Staring IPnetwork equipments backup\n";

print "$TIMESTAMP: Calling expect script ...\n";
system("$BACKUP_SCRIPT");

print "$TIMESTAMP: Checking last generated files to be sent to OMBS (10.1.90.10)\n";
#get the last files generated
@files = `find $FILES_DIR -newermt "$HOW_OLD" -type f -name "$PATTERN" -print`;

#get the last backup
$BKP_DIR_PATH = `find $ONSITE_BKP_DIR -newermt "$HOW_OLD" -type d -name "$BKP_DIR_PATTERN" -print`;
chomp($BKP_DIR_PATH);
print "$TIMESTAMP: Backup dir path to be sent to OMBS: $BKP_DIR_PATH\n";

#if there are some files
if (@files) {

	foreach (@files) {
		chomp($_);
		#get the file size
		$filename = "$_";
		$file_size = (stat $filename)[7]+0;

		#check if generated file has content in it
		#15000 bytes was chosen as threshold
		#if file size is ok, then will be sent via sftp
		if ($file_size > 15000) {
		
			print "$TIMESTAMP: $filename is ok and ready to be sent to OMBS\n";
		
		#otherwhise will print error	
		} else {
		
			print "$TIMESTAMP: There was a problem with $filename! It's size is smaller than expected!\n";

		}

	}#end of foreach

    print "$TIMESTAMP: Sending backup: $BKP_DIR_PATH to OMBS\n";
    $send_cmd = "scp -r $BKP_DIR_PATH $OMBS_USERNAME\@$OMBS_SERVER:$OMBS_DIR";
    $cmd_exec = `$send_cmd`;

#if we don't have as many files as hosts defined in expext script will exit	
} else {

	printf "$TIMESTAMP: There was a problem I didn't get any generated files by the expect script!\n";

}

print "$TIMESTAMP: Done.\n";
