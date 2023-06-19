#Import necessary libraries
from flask import Flask, jsonify,request
import cv2 
import numpy as np
from numpy import asarray
import pandas as pd
import os
#Initialize the Flask app

scanned_users = set()
try:
    file = 'passes_list.xlsx'
    df_regular = pd.read_excel(file,'Regular')
    df_early = pd.read_excel(file,'Early')
    df_vip = pd.read_excel(file,'VIP')
except:
    pass

app = Flask(__name__)
    
@app.route('/')
def index():
    return "NUVYUVA REST API"

@app.route('/Refresh_Excel', methods=['POST'])
def Refresh_Excel():
    global df_regular
    global df_early
    global df_vip    
    if request.method == 'POST':
        try:            
            trial = request.files['excel']
            trial_df = pd.read_excel(trial,'Regular')
            trial_df = pd.read_excel(trial,'Early')
            trial_df = pd.read_excel(trial,'VIP')
        except Exception as e:
            return jsonify("upload .xlsx file with key param as 'excel' and with Regular, Early and VIP sheets")
        try:            
            excel = request.files['excel']
            df_regular = pd.read_excel(excel,'Regular')
            df_early = pd.read_excel(excel,'Early')
            df_vip = pd.read_excel(excel,'VIP')
            return "Successful"
        except Exception as e:
            return jsonify("Error in updating dataframes, please upload excel file with .xlsx extension and 'Regular', 'Early', 'VIP' sheets"+str(e))
    return jsonify("Unsuccessful, POST method required")

@app.route('/Reset', methods=['GET'])
def Reset():    
    global scanned_users
    scanned_users = set()
    return jsonify("Reset Done")
    
@app.route('/GetData_from_QR', methods=['POST'])
def GetData_from_QR():
    global scanned_users
    global df_regular
    global df_early
    global df_vip
    try:
        if request.method == 'POST':
            filename = request.files['image']
            response = filename.read()
            frame = cv2.imdecode(np.fromstring(response, np.uint8), cv2.IMREAD_COLOR)
            detector = cv2.QRCodeDetector()
            data, vertices_array, binary_qrcode = detector.detectAndDecode(frame) 
            uuid=''
            json_response = 'No data found'
            status = False
            if(not len(data)):
                return json_response
            if data in scanned_users:
                status = True
            if vertices_array is not None:
                uuid=data
                scanned_users.add(uuid)
            typ = 'No'            
            if(len(df_regular[df_regular['uuid5'] == uuid])):
                typ = 'Regular'
                row = df_regular[df_regular['uuid5'] == uuid].to_dict('records')[0]
            elif(len(df_early[df_early['uuid5'] == uuid])):
                typ = 'Early'
                row = df_early[df_early['uuid5'] == uuid].to_dict('records')[0]
            elif(len(df_vip[df_vip['uuid5'] == uuid])):
                typ = 'VIP'
                row = df_vip[df_vip['uuid5'] == uuid].to_dict('records')[0]
            row['type'] = typ
            row['repeat'] = status
            row['total'] = len(scanned_users)
            return row
        return jsonify("Put a POST Request")
    except Exception as e:
        return jsonify("Error occured ,"+str(e))


@app.route('/ScanQR', methods=['POST'])
def ScanQR():
    try:        
        filename = request.files['image']
        response = filename.read()
        frame = cv2.imdecode(np.fromstring(response, np.uint8), cv2.IMREAD_COLOR)
        detector = cv2.QRCodeDetector()
        data, vertices_array, binary_qrcode = detector.detectAndDecode(frame) 
        if vertices_array is not None:
            return jsonify(data)
        return jsonify('No uuid found')
    except Exception as e:
        return jsonify('Error in Detecting QR, '+str(e))

@app.route('/GetData_from_uuid', methods=['POST'])
def GetData_from_uuid():
    try:
        global scanned_users
        global df_regular
        global df_early
        global df_vip
        uuid = request.args.get('uuid')              
        status = False
        if uuid in scanned_users:
            status = True        
        if len(uuid):
            scanned_users.add(uuid)
        typ = 'No'         
        if(len(df_regular[df_regular['uuid5'] == uuid])):
            typ = 'Regular'
            row = df_regular[df_regular['uuid5'] == uuid].to_dict('records')[0]
        elif(len(df_early[df_early['uuid5'] == uuid])):
            typ = 'Early'
            row = df_early[df_early['uuid5'] == uuid].to_dict('records')[0]
        elif(len(df_vip[df_vip['uuid5'] == uuid])):
            typ = 'VIP'
            row = df_vip[df_vip['uuid5'] == uuid].to_dict('records')[0]
        row['type'] = typ
        row['repeat'] = status
        row['total'] = len(scanned_users)
        return row
    except Exception as e:
        return jsonify('Error in Fetching data from UUID, '+str(e))
    
@app.route('/GetData_from_Srno', methods=['GET'])
def GetData_from_Srno():
    global df_regular
    global df_early
    global df_vip
    try:
        srno = request.args.get('Srno')    
        if(len(df_regular[df_regular[df_regular.columns[0]] == int(srno)])):
            return df_regular[df_regular[df_regular.columns[0]] == int(srno)].to_dict('records')[0]
        elif(len(df_early[df_early[df_early.columns[0]] == int(srno)])):
            return df_early[df_early[df_early.columns[0]] == int(srno)].to_dict('records')[0]
        elif(len(df_vip[df_vip[df_vip.columns[0]] == int(srno)])):
            return df_vip[df_vip[df_vip.columns[0]] == int(srno)].to_dict('records')[0]
    except Exception as e:
        return jsonify('Error in Fetching data from Sr.No, '+str(e))   
    
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), use_reloader=False)
