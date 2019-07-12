win__author__ ='ji'
__status__='under development'
__version__='0.1.0'
__date__='July 12, 2019'


def bcc(self:str)->str:
    '''
    BCC conversion function
    Returns in 2 letters as BCC in str in upper case
    This BCC works with Panasonic PLC and laser measurement
    '''
    i=0
    BCC_1='00'

    while i<len(self):
        BCC_1= hex(int(BCC_1,16) ^ int(hex(ord(self[i]))[2:],16))
        i+=1

    bcc_ret=BCC_1[2:].upper()
    if len(bcc_ret)==1:
        bcc_ret='0'+bcc_ret
      
    return bcc_ret


# Command: READ measurement value.
# OUT='3'=read OUT1 value
# OUT='4'=read OUT2 value
# Return value: str
def read_measurement_value(OUT:str='1')->str:

    OUT='3' if OUT !='2' else '4'
        
    command='%EE#RMD'+OUT
    return command+bcc(command)+'\r'


def read_intensity_value(HEAD:str='A')->str:

    HEAD='1' if HEAD != 'B' else '2'
        
    command='%EE#RID'+HEAD
    return command+bcc(command)+'\r'


def read_buffering_last(OUT:str='1')->str:
    OUT='3' if OUT !='2' else '4'
        
    command='%EE#RLD'+OUT
    return command+bcc(command)+'\r'
  
def read_buffering_data(OUT:str='1',start_adr='1',end_adr='100')->str:
    OUT='3' if OUT !='2' else '4'

    start_adr='{:0>5}'.format(start_adr)
    end_adr='{:0>5}'.format(end_adr)
        
    command='%EE#RLA'+ OUT + start_adr + end_adr
    return command+bcc(command)+'\r'


#CONTROL=1: Stop emissoin (Defalult)
#CONTROL=0: Start emissoin
def write_laser_emission(HEAD:str='A',CONTROL:str='OFF')->str:
    HEAD='1'if HEAD!= 'B' else '2'
    CONTROL='1' if CONTROL!= 'ON' else '0'

    command='%EE#WLR'+HEAD+'0000'+CONTROL
    return command+bcc(command)+'\r'


def write_zero_set(OUT:str='1',SET:str='ON')->str:
    OUT='3' if OUT !='2' else '4'
    SET='1' if SET!='OFF' else '0'
    
    command='%EE#WZS'+OUT+'0000'+SET
    return command+bcc(command)+'\r'


def write_averaging_number(OUT:str='1',NUMBER:str='8')->str:
    OUT='3' if OUT !='2' else '4'

#Check if NUMBER is int value or not.
    try:
        num=abs(int(NUMBER))
    except:
        num=8
        
    num=8 if num > 16 else num
    s_number=str(num)
    
    if len(s_number)==1:
        s_number='0'+s_number
    
    command='%EE#WAV'+OUT+'000'+ s_number
    return command+bcc(command)+'\r'


def write_calibration_current(AB:str='A',HEAD:str='A',VALUE:str='+005.000000')->str:
    AB='A'if AB!= 'B' else 'B'
    HEAD='1'if HEAD!= 'B' else '2'
    VALUE=correct_hlc2_value(VALUE)

    if len(VALUE)==11:
        command='%EE#WC'+AB+HEAD+VALUE
        command=command+bcc(command)+'\r'
    else:
        command='ERR: The length of VALUE was not 11 characters.'
    return command

def write_calibration_value(ab:str='a',HEAD:str='A',VALUE:str='+005.000000')->str:
    ab='A'if ab!= 'b' else 'B'
    HEAD='1'if HEAD!= 'B' else '2'
    VALUE=correct_hlc2_value(VALUE)

    if VALUE[0:3]!='ERR':
        command='%EE#WH'+ab+HEAD+VALUE
        command=command+bcc(command)+'\r'
    else:
        return VALUE
    
    return command


def write_calibration_start(HEAD:str='A',START:str='start')->str:
    """
    <<Caution>> Start(1) or Cancel(2) takes about 3 seconds.
                Please set time out long enough.

    """

    HEAD='1'if HEAD!= 'B' else '2'

    if START.lower() in {'start','1'}:
        START='1'
    elif START.lower() in {'stop','0'}:
        START='0'

    elif START.lower() in {'cancel','2'}:
        START='2'
    else:
        START='0'

    command='%EE#WCE'+HEAD+'0000'+START
    return command+bcc(command)+'\r'


def write_buffering_start(START:str='Start')->str:
    
    if START.lower() in {'start','1'}:
        START='1'
    elif START.lower() in {'stop','0'}:
        START='0'
    
    command='%EE#WBS00000'+START
    return command+bcc(command)+'\r'

def write_buffering_selfstop(arg:str='1')->str:
    arg='1' if arg !='0' else '0'
       
    command='%EE#WSS00000'+arg
    return command+bcc(command)+'\r'


def read_response(arg:str)->str:
    '''
    Checks response based on 2 characters as command in the response
    and parce necessary characters as value or data.
    '''
    err_chk, response=error(arg)
    if err_chk=='OK':
        command=response[5:7]
        if command=='MD':      #Measurement value
            read_response=response[7:18]
        #HEAD command
        elif command=='MM':    #Diffuese(0) or Specular (1)
            read_response=response[11:12]
        elif command=='FB':    #Light intensity setting
            read_response=response[10:12]
        elif command in {'EA','EB','PA','PB'}:    #Area a 001~512
            read_response=response[9:12]
        elif command=='FC':    #Auto intensity status
            read_response=response[11:12]
        elif command=='HC':    #Alarm delay
            read_response=response[7:12]
        elif command=='SM':    #Target surface type
            read_response=response[11:12]
        elif command=='ID':    #Light intensity
            read_response=response[7:12]
        elif command=='BF':    #Near or Far
            read_response=response[11:12]
        elif command in {'CA','CB','HA','HB'}: #Calibration vallues
            read_response=response[7:18]
        elif command=='LR':     #Laser ON/OFF
            read_response=response[11:12]
        elif command=='TH':     #Peak sensitivity
            read_response=response[9:12]
        elif command=='MF':     #Median filter
            read_response=response[11:12]
        #OUT command
        elif command in {'OS','MN'}:  #Measurement operation, Transparent object
            read_response=response[10:12]
        elif command=='GK':     #Diffraction calculation Valid
            read_response=response[11:12]
        elif command=='GR':     #Diffraction index
            read_response=response[7:18]
        elif command in {'ZS','TI','RS','HD','HM','FL'}:     #Zero set, Timing, Reset, Hold, Mode, Filter
            read_response=response[11:12]
        elif command in {'AV','CO'}:     #Average, Cut off freq
            read_response=response[10:12]
        elif command in {'MK','ML','HL','LL','EH','EL'}:     #Gain, Offset, Limits, Hys
            read_response=response[7:18]
        elif command in {'AH','AL','VH','VL','FM','DA'}:     #Analog scaling, DA voltage
            read_response=response[7:18]
        elif command in {'AS','AA','AD','AC'}:     #Analog scaling status, AD at alarm
            read_response=response[11:12]
        elif command in {'OA','OB','HI','GO','LO'}:     #Alarm status, Strobe out status
            read_response=response[11:12]
        #COMMON command
        elif command in {'SP','IM','IC','OF'<'XT'}:  #Measurement operation, Transparent object
            read_response=response[11:12]
        elif command == 'MA':     #OUT1, OUT2
            read_response=response[7:29]
        elif command == 'MB':     #OUT1, OUT2
            read_response=response[7:35]
        #SYSTEM command
        elif command =='YU':  #Priority of Memory select
            read_response=response[11:12]
        elif command == 'MC':  #Selected memory, Destination memo to copy
            read_response=response[10:12]
        elif command in {'SA','SB','SC','SD','SE','KS','UT'}:  #RS232C baudrate, data length, Parity
            read_response=response[11:12]
        #Buffering command
        elif command in {'SS','BD','TT','TR','BS','TS'}:  #Self stop ON=1, oFF=0
            read_response=response[11:12]
        elif command in {'BR','BD','TT'}:  #Buffering rate, type, Mode
            read_response=response[10:12]
        elif command in {'BC','TP','SR','LD','LE'}:    #Buffering # of logging
            read_response=response[7:12] 
        elif command=='TL':    #Trigger delay
            read_response=response[7:18]        
        elif command=='LA':    #Buffer data read
            res_len=len(response)
            read_response=response[7:res_len-4]
            
        else:
            read_response=''
    else:
        read_response=err_chk

    return read_response


def write_response(arg:str)->str:
    return error(arg)[0]
    


def error(arg:str)->(str,str):
    """
    Cleans the response string taking out 'b' or '\'' and store the response as str
    Checks BCC if the BCC is not **
    If there is any error, returns the error code and the explanation.
    Returns 'OK' or 'ERR' in the first three characters.
    """
    
    response:str=arg.replace('b','').replace('\'','')
    error_chk=''
    
    if response[3]=='!':
        error_code=response[4:6]
        if error_code=='01':
            error_chk='ERR:01: First 4 characters are not %%EE$'

        elif error_code=='02':
            error_chk='ERR:02: The command doesn\'t exist.'

        elif error_code=='03':
            error_chk='ERR:03: The 4th character is not R or W.'

        elif error_code=='05':
            error_chk='ERR:05: The requested lenght of data is out of the range.'

        elif error_code=='07':
            error_chk='ERR:07: The requested data is out of the range.'

        elif error_code=='08':
            error_chk='ERR:08: BCC error at slave side.'

        elif error_code=='11':
            error_chk='ERR:11: Communication error. Parity error etc.'

        elif error_code=='20':
            error_chk='ERR:20: Cannot execute with the specified calibration or scaling for analog ouput.'
        
        elif error_code=='21':
            error_chk='ERR:21: Cannot change configuration of buffering while buffering is being executed.'
        
        elif error_code=='22':
            error_chk='ERR:22: Cannot start buffering with incorrect configuration for buffering.'
        
        elif error_code=='23':
            error_chk='ERR:23: Cannot read buffering data while buffering is being executed.'
        
    else:
        if response[3]=='$':
            error_chk='OK'

    arg_len=len(response)
    
    if arg_len>5 or response[arg_len-4:arg_len-2]!='**' :
        if response[arg_len-4:arg_len-2] !=bcc(response[0:arg_len-4]):
            error_chk='ERR:BCC error'

    return error_chk,response


def correct_hlc2_value(arg:str)->str:
    """
    Corrects a value(arg) as the acceptable format to write as distance.
    Making sure that the vallue to write doesn't exceed +/-950mm
    The format must follow -950.000000 to +950.000000
    Signed.  3 digits above decimal point. 6 digits below decimal point.

    """
    try:
        if float(arg)>950 or float(arg)<-950:
            return 'ERR: Argument exceeded acceptable range from -950 to +950.'
    except ValueError:
        return 'ERR: Argument was not a number'


    if arg[0] in {'+','-'}:
        sign=arg[0]
        arg=arg.strip('+')
        arg=arg.strip('-')
    else:
        sign='+'
    
    if '.' in arg:
        upper_val,lower_val=arg.split('.')
    else:
        upper_val=arg
        lower_val='000000'
    upper_val='{:0>3}'.format(upper_val)
    lower_val='{:0<6}'.format(lower_val)
    if len(lower_val)>6:
        lower_val=lower_val[0:6]

    return sign+upper_val+'.'+lower_val


'''
Preparing understandable value from just index value in response for each response
'''
INSTALL_MODE=['Diffuse reflection','Specular reflection']
EMISSION_LEVEL=['Auto','0.04%','0.05%','0.06%','0.08%','0.11%','0.14%','0.18%',
            '0.24%','0.31%','0.40%','0.53%','0.68%','0.89%','1.16%','1.50%',
            '1.95%','2.54%','3.3%','4.29%','5.58%','7.25%','9.43%','12.3%',
            '15.9%','20.7%','26.9%','35.0%','45.5%','59.2%','76.9%','100%']
EMISSION_SEARCH=['None','Execute','Searching']
MEASUREMENT_MODE=['Diffuse(Standard)',
                  'Specular(Standard)',
                  'Metal1',
                  'Metal2',
                  'Penetration',
                  'Glass',
                  'Glass(Patterned)']
MEASUREMENT_DIRECTION=['Near','Far']
LASER_CONTROL=['Laser ON','Laser OFF']
MEDIAN_FILTER       =['OFF',
                      '7 points',
                      '15 points',
                      '31 points']
OUTPUT_SELECTION    =['A',
                      'B',
                      '-A',
                      '-B',
                      'A+B',
                      '-(A+B)',
                      'A-B',
                      'B-A',
                      'A (Transparent)',
                      'B (Transparent)',
                      '-A (Transparent)',
                      '-B (Transparent)',
                      'A1+B1 (Transparent)',
                      '-A1+B1 (Transparent)',
                      'A1-B1 (Transparent)',
                      'B1-A1 (Transparent)']
TRANSPARENT_OBJECT  =['Distance to 1st surface',
                      'Distance to 2nd surface',
                      'Distance to 3rd surface',
                      'Distance to 4th surface',
                      'Upper Limit surface',
                      'Thickness of 1st to 2nd surface',
                      'Thickness of 1st to 3rd surface',
                      'Thickness of 1st to 4th surface',
                      'Thickness of 1st to Up surface',
                      'Thickness of 2nd to 3rd surface',
                      'Thickness of 2nd to 4th surface',
                      'Thickness of 2nd to Up surface',
                      'Thickness of 3rd to 4th surface',
                      'Thickness of 3rd to Up surface',
                      'Thickness of 4th to Up surface']
OFF_ON                  =['OFF','ON']
REFRACTION_CALCULATION  =OFF_ON
ZERO_SET                =OFF_ON
TIMING                  =OFF_ON
RESET                   =OFF_ON                    
HOLD                    =OFF_ON
ANALYSIS_MODE       =['Normal',
                      'Peak',
                      'Bottom',
                      'Peak to Peak']
FILTER_OPERATION    =['Moving average',
                      'Low pass filter',
                      'High pass filter']
AVERAGING_TIME      =['x1','x2','x4','x8','x16','x32','x64','x128','x256','512',
                      'x1,024','x2,048','x4,096','x8192','x16,384','x32,768','x65,536']
CUTOFF_FREQUENCY    =['1Hz','2Hz','4Hz','10Hz','20Hz','40Hz',
                      '100Hz','200Hz','400Hz','1kHz','2kHz']
ANALOG_SCALING      =['None',
                      'Execute',
                      'Cancel']
ANALOG_OUT_ALARM    =['Hold previous value',
                      'Fixed value']
DIGITAL_OUT_ALARM   =ANALOG_OUT_ALARM
ALARM_OUT_DELAY     =OFF_ON
DIGIT_NUM_VALUE     =['6 digits below decimal point',
                      '5 digits below decimal point',
                      '4 digits below decimal point',
                      '3 digits below decimal point',
                      '2 digits below decimal point',
                      '1 digits below decimal point']
ALARM_OUT_READ      =['Alarm OFF',
                      'Measurement alarm',
                      '',
                      '',
                      '',
                      'Sensor head A unconnected',
                      'Connected head unadapted',
                      'Head connection check error']
STROBE_OUT_READ     =['Strobe OFF',
                      'Strobe ON']

JUDGMENT_OUT_HI_RD  =['Judgement output HI OFF',
                      'Judgement output HI ON']
JUDGEMENT_OUT_GO_RD =['Judgement output GO OFF',
                      'Judgement output GO ON']
JUDGEMENT_OUT_LO_RD =['Judgement output LO OFF',
                      'Judgement output LO ON']
SAMPLING_CYCLE      =['10us','20us','40us','100us','200us','400us','1ms','2ms']
TERMINAL_INPUT_CTRL =['Independent','All']
CHATTERING_PREVENT  =['OFF','ON1','ON2']
JUDGE_OUT_OFF_DELAY =['OFF','2ms','10ms','100ms','Hold']
INTERFERENCE_PREVENT=OFF_ON
PRIORITY_MEM_CHANGE =['Command',
                      'Input terminal']
RS232C_BAUDRATE     =['9600bps',
                      '19.2kbps',
                      '38.4kbps',
                      '115.2kbps']
RS232C_DATA_LENGTH  =['7bit',
                      '8bit']
RS232C_PARITY_CHECK =['Even',
                      'Odd',
                      'None']
RS232C_OUT_MODE     =['Handshake',
                      'Timing',
                      'Continuous']
RS232C_OUT_TYPE     =['OUT1 & OUT2',
                      'OUT1 only',
                      'OUT2 only']
DISP_REFRESH_SPEED  =['Fast',
                      'Standard',
                      'Slow',
                      'Very Slow']
DISPLAY_UNIT        =['mm',
                      'um']
BUFFER_SELF_STOP    =OFF_ON
BUFFER_MODE         =['Continuous',
                      'Trigger',
                      'Timing',
                      'Sample Trigger']
BUFFER_TYPE         =['OUT1 & OUT2',
                      'OUT1 only',
                      'OUT2 only']
BUFFER_RATE         =['1',
                      '1/2',
                      '1/4',
                      '1/8',
                      '1/16',
                      '1/32',
                      '1/64',
                      '1/128',
                      '1/256',
                      '1/512',
                      '1/1024',
                      '1/2048',
                      '1/4096',
                      '1/8192',
                      '1/16384',
                      '1/32768']
BUFFER_TRIGGER_COND =['at ON of timing input',
                      'at HI',
                      'at LO',
                      'at HI or LO',
                      'when HI became to GO',
                      'when LO became to GO',
                      'when HI or LO became to GO',
                      'at Alarm occurred',
                      'at Alarm released']
BUFFER_OPERATION    =['Stop',
                      'Start']
BUFFER_READOUT      =['Buffering none',
                      'Waiting for trigger',
                      'Accumulating',
                      'Accumulation completed']
