import ctypes
import datetime

def skip_time_4h():
    print("⏳ [Time-Skip Protocol] Jumping forward 4 Hours to grow crops instantly...")
    
    class SYSTEMTIME(ctypes.Structure):
        _fields_ = [
            ("wYear", ctypes.c_int16),
            ("wMonth", ctypes.c_int16),
            ("wDayOfWeek", ctypes.c_int16),
            ("wDay", ctypes.c_int16),
            ("wHour", ctypes.c_int16),
            ("wMinute", ctypes.c_int16),
            ("wSecond", ctypes.c_int16),
            ("wMilliseconds", ctypes.c_int16)
        ]
        
    system_time = SYSTEMTIME()
    
    # الحصول على الوقت الحالي (بتوقيت جرينتش)
    now = datetime.datetime.utcnow()
    # إضافة 4 ساعات
    new_time = now + datetime.timedelta(hours=4)
    
    system_time.wYear = new_time.year
    system_time.wMonth = new_time.month
    system_time.wDayOfWeek = new_time.weekday()
    system_time.wDay = new_time.day
    system_time.wHour = new_time.hour
    system_time.wMinute = new_time.minute
    system_time.wSecond = new_time.second
    system_time.wMilliseconds = new_time.microsecond // 1000
    
    # تنفيذ أمر التغيير في نواة الويندوز
    result = ctypes.windll.kernel32.SetSystemTime(ctypes.byref(system_time))
    
    if not result:
        print("❌ ERROR: Time skip failed! You MUST run this script as Administrator (صلاحيات المسؤول).")
        return False
    else:
        print("✅ SUCCESS: Time traveled 4 hours into the future! Crops should be fully grown.")
        return True