@echo off

SET TEMP=temp

call venv/scripts/activate

@REM python app.py --deepspeed --rvc
python app.py  --rvc

pause