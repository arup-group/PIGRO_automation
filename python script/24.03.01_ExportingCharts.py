import os
import sys
import win32com.client 
from win32com.client import Dispatch
import shutil


def create_diag_folder(directory):

    if os.path.exists(directory):
        # Elimina la directory e tutti i file al suo interno
        shutil.rmtree(directory)
        os.makedirs(directory)
    elif not os.path.exists(directory):
        # Se non esiste, crea la cartella
        os.makedirs(directory)

    """
    if not os.path.exists(directory):
        # Se non esiste, crea la cartella
        os.makedirs(directory)
    """


def v3_export_image(workbook_file_name, directory):

    app = win32com.client.Dispatch("Excel.Application")
    # It's important to use the absolute path, it won't work with a relative one.
    

    workbook = app.Workbooks.Open(Filename= workbook_file_name)
    
    for i, sheet in enumerate(workbook.Worksheets):
        #sheets_name = []
        #sheets_name.append(sheet.NAme)

        #for name in sheets_name:

        worksheet = workbook.Sheets(sheet.Name) #("NomeDelFoglio")

        

        app.WindowState = -4137 #win32com.client.constants.xlMaximized #   constants.xlMaximized

        worksheet.Activate()

        app.Visible = True

        app.DisplayAlerts = True

        for ind, chartObject in enumerate(worksheet.ChartObjects()):
            #print(sheet.Name + ':' + chartObject.Name)
            #print(str(directory + "\\" + str(i+1) + "_" + str(sheet.Name) + ".png"))

            # It's important to use the absolute path, it won't work with a relative one.
            print(directory + "\\" + str(worksheet.Name)  + "_" + str(ind+1) + ".png")

            chartObject.Chart.Export(directory + "\\" + str(worksheet.Name)  + "_" + str(ind+1) + ".png")

    workbook.Close(SaveChanges=False, Filename=workbook_file_name)
    

# Ottieni il percorso della directory corrente (dove si trova il codice)
    
#IF IT'S .EXE
current_directory = os.path.dirname(sys.executable) 
#IF IT'S PYTHON 
#current_directory = os.path.dirname(os.path.abspath(__file__))

# Definisci i nomi delle sottocartelle
diagrams_folder = os.path.join(current_directory, "DIAGRAMS")
json_folder = os.path.join(current_directory, "JSON")

diagrams_names = []
json_names = []
corresponding_files = []

try:
    # Ottieni i nomi dei file nella cartella DIAGRAMS
    for diagname in os.listdir(diagrams_folder):
        diagrams_names.append(diagname)
        #print(diagname)

    # Ottieni i nomi dei file nella cartella JSON
    for jsonname in os.listdir(json_folder):
        json_names.append(jsonname)
        #print(jsonname)

    # Cerca i file corrispondenti
    for json_name in json_names:
        for diag_name in diagrams_names:
            if diag_name.startswith(json_name[:-5]):  # Confronto usando startswith
                json_path = os.path.join(json_folder, json_name)
                diag_path = os.path.join(diagrams_folder, diag_name)
                corresponding_files.append([json_path, diag_path])
                break  # Esci dal loop interno se trovi una corrispondenza

except Exception as ex:
    print(f"Si è verificato un errore: {ex}")


iterat_numb = (str(len(corresponding_files)))

print("There are " + str(iterat_numb) + " iterations associated with the given excel input.")



    
for file_ind, files in enumerate(corresponding_files):
    # Fornisci la directory del file JSON

    json_directory = files[0]
    
    # Fornisci la directory del file Excel esistente
    existing_excel_file = files[1]

    #print(existing_excel_file + ".xlsx")

    try:
        # Carica il contenuto del file JSON
        # Carica il file Excel esistente 
        if existing_excel_file.endswith(".xlsx"):
            existing_excel_file_correct= existing_excel_file
        else:
            existing_excel_file_correct= existing_excel_file + ".xlsx"
            
        diag_directory = existing_excel_file_correct
        

        create_diag_folder(directory= diag_directory[:-5])


        v3_export_image(workbook_file_name= diag_directory, directory= diag_directory[:-5])

    except FileNotFoundError:
        print(f"File non trovato: {json_directory}")
    except KeyError as e:
        print(f"La chiave '{e.args[0]}' non è presente nel file JSON.")
    except json.JSONDecodeError as e:
        print(f"Errore nel decodificare il file JSON: {e}")
    except Exception as ex:
        print(f"Si è verificato un errore: {ex}")


    print( str(file_ind + 1) + " out of " + str(iterat_numb) + " iterations exported.")

print("The diagrams have been exported here: " + str(diagrams_folder))