
REM provide -i and -w to gh script
C:\ARUP\proj\PIGROphase2\25.02.27\.venv\Scripts\python.exe "C:\ARUP\proj\PIGROphase2\25.02.27\main_folder_test\txt_path.py" -i "C:\ARUP\proj\PIGROphase2\25.02.27\main_folder_test\test_path\input" -w "C:\ARUP\proj\PIGROphase2\25.02.27\main_folder_test\test_path\work"


REM open GH script in the branch folder, pass -i, -w and run PIGRO analysis
set path= C:\ARUP\proj\PIGROphase2\25.02.27\main_folder_test\PIGRO_Script
"%ProgramFiles%\Rhino 7\System\Rhino.exe" /nosplash /runscript="-grasshopper editor load document open %path%.gh _enter exit _enter"


REM Run python to generate charts and excel, providing -i and -w
C:\ARUP\proj\PIGROphase2\25.02.27\.venv\Scripts\python.exe "C:\ARUP\proj\PIGROphase2\25.02.27\main_folder_test\PIGRO_automation.py" -i "C:\ARUP\proj\PIGROphase2\25.02.27\main_folder_test\test_path\input" -w "C:\ARUP\proj\PIGROphase2\25.02.27\main_folder_test\test_path\work"

