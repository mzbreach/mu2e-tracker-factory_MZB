import os
import csv

'''
    createArrayOfFiles works to fill a python list with
    all of the LPAL csv files found within data/Loading Pallets
    
    This program operates on a slightly modified parent directory
    containing only LPAL csv files without the extra 'Straw Resistances LPAL' directory
    or any extra .csv or .py files.
'''
def createArrayOfFiles(path):
    return os.listdir(path)

'''
    readInCSV creates a two-dimensional python list with indices populated with
    the data within a csv file (given as a function parameter)

    Ex:         
    1,2,3   -->   [ [1,2,3],
    4,5,6           [4,5,6] ]

    This function is specifically used to ingest the csv file generated from SQL queries
    within the DB that contains the following data:

        panel_Num, lower_LPAL_Num, lowerLPAL_straw_location, lower_LPALID, upper_LPAL_Num,
        upper_straw_location, upper_LPALID, comments
'''
def readInCSV(path):
    #open the file
    dataFile = open(path, 'r')
    #use the reader method within the csv lib to create a reader object that allows iteration
    dataReader = csv.reader(dataFile, delimiter = ',')
    #create list to return
    data = []
    #iterate through and add each row (from reader object calls within for loop params) to the list
    for row in dataReader:
        data.append(row)
    dataFile.close()
    return data

'''
    createOutput produces a .csv file with given file name and two given arrays:
        1. A list of length 2 lists containing a pair of LPAL nums and LPAL IDs
        2. A 2d list containing the "master" csv file
    
    This produces the "final" version (pending continued extrapolation upon specific 
    reasoning behind LPAL num choices)
'''
def createOutput(fname, fileArray, infoArray):
    f = open(fname, 'w')
    i = 0
    for row in infoArray:
        j = 0
        for column in row:
            #Check to see if the current column within the SQL generated csv
            #is a LPAL Num; if so, enter the statement and search for its corresponding
            if((j == 1 or j == 4) and (i != 0)):
                for pair in fileArray:
                    if(int(pair[0]) == int(column)):
                        row[j + 2] = pair[1]
            if(column == "-1" or column == "0"):
                f.write("None")
            else:
                f.write(str(column))
            if(j != len(row) -1):
                f.write(',')
            if(j == len(row)-1 or j == len(row) -2):
                f.write("\"")
            j+=1
        f.write("\n")
        i+=1
    f.close()
            
'''
    main calls the respective functions and formats the file list into a list of pairs of LPAL nums and IDs
'''
def main():
    files = createArrayOfFiles("C:/Users/mu2e/Documents/matthewWorkSpace/inProgress/loading_palets")
    finalList = []
    for x in files:
        lpalNum = int(x[4:8])
        lpalID = int(x[15:17])
        lpalNumAndID = [lpalNum, lpalID]
        finalList.append(lpalNumAndID)

    csvInfo = readInCSV("C:/Users/mu2e/Documents/matthewWorkSpace/inProgress/panel_and_LPAL_info_MERGED_AND_CLEANED_V2.csv")
    createOutput("panel_and_LPAL_info_FINAL.csv", finalList, csvInfo)

if __name__ == "__main__":
    main()