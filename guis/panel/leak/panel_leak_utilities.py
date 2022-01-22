import pandas as pd
import datetime
import sqlite3

################################################################################
# Constants
################################################################################
# Unit conversion factor for inches of water to psi.
kINCHES_H2O_PER_PSI = 27.6799048

# Unit conversion factor for PSI change per day to sccm
kPSI_PER_DAY_TO_SCCM = 0.17995993587933934

kPROCESSES = list(range(1, 9))

################################################################################
# Helper functions
################################################################################
def ConvertInchesH2OToPSI(pressure_inches_h2O):
    return pressure_inches_h2O / kINCHES_H2O_PER_PSI


################################################################################
# READ INPUT
# Read the raw data (old or new format) into a dataframe
# dataframe format:
# TIME(DAYS)  FillPSIA  RefPSIA  PRESSURE(PSI)  BOX TEMPERATURE(C)  ROOM TEMPERATURE(C)  Heater%
################################################################################
def ReadLeakRateFile(infile, is_new_format="true"):
    if is_new_format:
        # read input file
        df = pd.read_csv(infile, engine="python", header=1, sep="\t")

        # remove whitespace from column headers
        df.columns = df.columns.str.replace(" ", "")

        # convert pressure from inches of water to psi
        df['Diff"H2O'] = ConvertInchesH2OToPSI(df['Diff"H2O'])
        df = df.rename(columns={'Diff"H2O': "PRESSURE(PSI)"})

        # rename time
        df = df.rename(columns={"Elapdays": "TIME(DAYS)"})

        # rename temps
        df = df.rename(columns={"RoomdegC": "ROOM TEMPERATURE(C)"})
        df = df.rename(columns={"EncldegC": "BOX TEMPERATURE(C)"})

        ## make a new column: pressure/temp
        # df['PSI/degC'] = df["PRESSURE(PSI)"]/df["RoomdegC"]

        return df
    else:
        # read input file
        df = pd.read_csv(infile, engine="python", header=4, sep=",", encoding="cp1252")

        # remove whitespace from column headers
        df.columns = df.columns.str.replace(" ", "")
        df.columns = df.columns.str.replace("\t", "")
        df.columns = df.columns.str.replace(u"°", "")

        # convert pressure from inches of water to psi
        df["PRESSURE(INH20D)"] = ConvertInchesH2OToPSI(df["PRESSURE(INH20D)"])
        df = df.rename(columns={"PRESSURE(INH20D)": "PRESSURE(PSI)"})

        # rename temp
        df = df.rename(columns={"TEMPERATURE(C)": "BOX TEMPERATURE(C)"})

        # convert absolute time to elapsed days
        def get_time(time_str):
            """Converts a time string from the datafile to UNIX time."""
            if "." in time_str:
                # More than 1 day has passed
                days, time_s = time_str.split(".")
            else:
                # Less than 1 day has passed
                days = "0"
                time_s = time_str
            days = int(days)
            hours, minutes, seconds = map(int, time_s.split(":"))

            td = datetime.timedelta(
                days=days, hours=hours, minutes=minutes, seconds=seconds
            )
            total_seconds = int(round(td.total_seconds()))

            return total_seconds / 24 / 60 / 60

        df["TIME(hh:mm:ss)"] = df["TIME(hh:mm:ss)"].apply(get_time)
        df = df.rename(columns={"TIME(hh:mm:ss)": "TIME(DAYS)"})

        ## make a new column: pressure/temp
        # print(df.columns)
        # df['PSI/degC'] = df["PRESSURE(PSI)"]/df["ROOM TEMPERATURE(C)"]

        return df


################################################################################
# READ INPUT
# Read raw data from the database into a dataframe, structurally equivalent to that of ReadLeakRateFile, but with timestamps retained
# TIME(DAYS)    FILLPSIA    RefPSIA PRESSURE(PSI)   BOX TEMPERATURE(C)  ROOM TEMPERATURE(C) Heater%
################################################################################

def readLeakDb(panel, tag):
    leak_df = pd.DataFrame()
    
    #ensure that panel is type str
    panel = str(panel)
    
    
    con = sqlite3.connect('data/database.db')
    cursor = con.cursor()

    # acquire straw location
    cursor.execute("SELECT * FROM straw_location WHERE number='"+str(panel)+"' AND location_type='MN'")
    straw_location = str(cursor.fetchall()[0][0])
    
    # use straw location to acquire procedure
    cursor.execute("SELECT * FROM procedure WHERE straw_location='"+straw_location+"' AND station='pan8'")
    procedure = str(cursor.fetchall()[0][0])
        
    # use procedure and tag to acquire trial
    cursor.execute("SELECT * FROM panel_leak_test_details WHERE procedure='"+procedure+"' AND tag='"+tag+"'")
    trial = str(cursor.fetchall()[0][0])
        
    # use trial to acquire pertinent entries from measurement_panel_leak
    leak_df = pd.read_sql_query("SELECT * FROM measurement_panel_leak WHERE trial='"+trial+"'", con)
        
    # rename pertinent columns
    leak_df.rename(columns={"elapsed_days":"TIME(DAYS)"}, inplace=True)
    leak_df.rename(columns={"pressure_diff":"PRESSURE(PSI)"}, inplace=True)
    leak_df.rename(columns={"pressure_ref":"RefPSIA"}, inplace=True)
    leak_df.rename(columns={"pressure_fill":"FillPSIA"}, inplace=True)
    leak_df.rename(columns={"temp_box":"BOX TEMPERATURE(C)"}, inplace=True)
    leak_df.rename(columns={"temp_room":"ROOM TEMPERATURE(C)"}, inplace=True)
    leak_df.rename(columns={"heater_pct":"Heater%"}, inplace=True)
    
    # drop other columns
    leak_df.drop(columns=['id', 'trial'], axis=1, inplace=True)
        
    con.close()
        
    return leak_df


################################################################################
# returns a list of leak test tags for an inputted panel
################################################################################

def getLeakTags(panel):
    tag_list = []
    con = sqlite3.connect('data/database.db')
    cursor = con.cursor()
    
    # acquire straw location
    cursor.execute("SELECT * FROM straw_location WHERE number='"+str(panel)+"' AND location_type='MN'")
    straw_location = str(cursor.fetchall()[0][0])

    # use straw location to acquire procedure
    cursor.execute("SELECT * FROM procedure WHERE straw_location='"+straw_location+"' AND station='pan8'")
    result = cursor.fetchall()
    if len(result) > 0:
        procedure = str(result[0][0])

        
        # use procedure and tag to acquire trial
        cursor.execute("SELECT * FROM panel_leak_test_details WHERE procedure='"+procedure+"'")
        raw_list = cursor.fetchall()



        for i in raw_list: # sort out tags from raw_list and put in list to return
            tag_list.append(str(i[2]))
    
    return tag_list
        
    
    
    
    
    

    
    
    
    