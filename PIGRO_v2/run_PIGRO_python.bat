

set path= C:\ARUP\proj\PIGROphase2\25.02.27\main_folder_test\PIGRO_Script


"%ProgramFiles%\Rhino 7\System\Rhino.exe" /nosplash /runscript="-grasshopper editor load document open %path%.gh _enter"


REM Run python from venv.
C:\ARUP\proj\PIGROphase2\25.02.27\.venv\Scripts\python.exe "C:\ARUP\proj\PIGROphase2\25.02.27\main_folder_test\test_excel_3.py"


pause