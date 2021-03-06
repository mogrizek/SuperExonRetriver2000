'''
Created on Mar 6, 2012

@author: Ana
'''

###############################
###############################
# imports
from os import remove, system, path, makedirs, listdir;
import re;
import ConfigParser;
from subprocess import *;


###############################
###############################
#Tools configuration and setting paths
config_file = "../../anab.cfg"
config = ConfigParser.RawConfigParser()
config.read(config_file)
session_resource_path = config.get('Session resource', 'session_resource_path')
#the input file
descr_file_path = config.get('Ensembl cfg', 'descr_file')
descr_file_path = "%s/%s" % (session_resource_path, descr_file_path);
ensembldb = config.get('Ensembl cfg', 'ensembldb')
masked = config.get('Ensembl cfg', 'masked')
if (masked == 1): 
    masked = True
else:
    masked = False
# how much to expand
ens_expansion = int(config.get('Ensembl cfg', 'expansion'))

#the gene regions folder
gene_regions_path = config.get('Gene regions path', 'regions')
gene_regions_path = "%s/%s" % (session_resource_path, gene_regions_path)
# the tmp folder
tmp_folder = config.get('Gene regions path', 'temporary_sequences')
tmp_folder = "%s%s" % (session_resource_path, tmp_folder)
# expanded regions folder
expanded_regions_f = config.get('Gene regions path', 'expanded_regions')
expanded_regions_f = "%s%s" % (session_resource_path, expanded_regions_f)
# cached data status file
status_file = "%s.status" % tmp_folder

###############################
# create session dir, if not existing
if (not path.exists(session_resource_path)):
    makedirs(session_resource_path)
    
if (not path.exists(gene_regions_path)):
    makedirs(gene_regions_path)
    
if (not path.exists(expanded_regions_f)):
    makedirs(expanded_regions_f)
    
if (not path.exists(tmp_folder)):
    makedirs(tmp_folder)
    

###############################
###############################
# Input files
descr_file = open(descr_file_path, 'r')

###############################
###############################
# dictionaries
ensembl_ids = dict()        #keys - species name, values - all the neccessary information

###############################
###############################
# input file parsing
descr_file_lines = descr_file.readlines()
# all the variables
# mandatory:
species_name = ""
id_type = ""
sid = ""
# optional:
assembly = ""
beginning = 0
ending = 0
strand = 1

###############################
###############################
def generate_file_name (masked, species, id_type, id):
    file_name = "%s/%s/dna/" % (ensembldb, species.lower())
    tmp_file=""
    for file in listdir(file_name):
        if (file != "README"):
            tmp_file = file 
            break
    m = re.findall ('(.*).dna', tmp_file)   
    if (masked == True):
        file_name = "%s/%s.dna_rm." % (file_name, m[0])
    else :
        file_name = "%s/%s.dna." % (file_name, m[0])
    if (id_type == 'chromosome'):
        file_name = "%schromosome.%s.fa" % (file_name, id)
    else :
        file_name = "%stoplevel.fa" % (file_name)
    return file_name
   

###############################
###############################
# function for getting the normal gene regions
def get_gene_regions ():

    i = 0
    print "Get gene regions started"    
    for line in descr_file_lines:
        print line
        if (i%4 == 0):
            species_name = line.strip('\n')
            output_file_name = "%s/%s.fa" % (gene_regions_path, species_name)
            
        elif (i%4 == 2):
            
            parameters = line.strip('\n').split(' ')[1].split(':')
            database = generate_file_name(masked, species_name, parameters[0], parameters[2])
            print database
            if (int(parameters[5]) == -1) : # convert into fastacmd friendly format
                parameters[5] = str(2)
            sid = ""
            if (parameters[0] == "chromosome"):
                sid = "chrom%s" % parameters[2]
            else :
                sid = parameters[2]
                
            cmd = "fastacmd -d %s -s %s -S %s -L %s,%s -p F -o %s"  %       (database,          # database name
                                                                             sid,                # id
                                                                             parameters[5],     # strand
                                                                             parameters[3],     # seq beginning
                                                                             parameters[4],     # seq ending
                                                                             output_file_name)
            print (cmd)   
            system(cmd)
            print "Wrote data to %s" % output_file_name
        i = i+1
                
                
###############################
###############################
# function for getting the expanded gene regions
def get_expanded_gene_regions ():

    i = 0
    print "Get gene regions started"    
    for line in descr_file_lines:
        print line
        if (i%4 == 0):
            species_name = line.strip('\n')
            output_file_name = "%s/%s.fa" % (gene_regions_path, species_name)
            
        elif (i%4 == 2):
            
            parameters = line.strip('\n').split(' ')[1].split(':')
            database = generate_file_name(masked, species_name, parameters[0], parameters[2])
            print database
            if (int(parameters[5]) == -1) : # convert into fastacmd friendly format
                parameters[5] = str(2)
            sid = ""
            if (parameters[0] == "chromosome"):
                sid = "chrom%s" % parameters[2]
            else :
                sid = parameters[2]
                
            cmd = "fastacmd -d %s -s %s -S %s -L %d,%d -p F -o %s"  %       (database,          # database name
                                                                             sid,                # id
                                                                             parameters[5],     # strand
                                                                             max(0, int(parameters[3])-ens_expansion),     # seq beginning
                                                                             int(parameters[4])+ens_expansion,     # seq ending
                                                                             output_file_name)
            print (cmd)   
            system(cmd)
            print "Wrote data to %s" % output_file_name
        i = i+1

get_gene_regions()
