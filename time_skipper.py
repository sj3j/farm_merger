import ctypes
import datetime

def set_system_time(dt):
    """دالة مساعدة للتواصل مع نواة الويندوز وتغيير الوقت"""
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
    system_time.wYear = dt.year
    system_time.wMonth = dt.month
    system_time.wDayOfWeek = dt.weekday()
    system_time.wDay = dt.day
    system_time.wHour = dt.hour
    system_time.wMinute = dt.minute
    system_time.wSecond = dt.second
    system_time.wMilliseconds = dt.microsecond // 1000
    
    return ctypes.windll.kernel32.SetSystemTime(ctypes.byref(system_time))


def jump_forward_4h():
    """القفز للمستقبل لتحفيز إرسال الهدايا والمحاصيل"""
    print("⏳ [Time-Skip] Jumping forward 4 Hours to trigger inbox gifts...")
    now = datetime.datetime.utcnow()
    future_time = now + datetime.timedelta(hours=4)
    
    success = set_system_time(future_time)
    if not success:
        print("❌ ERROR: Time skip failed! Run script as Administrator.")
        return False
    print("✅ SUCCESS: Time traveled 4 hours into the future!")
    return True


def revert_to_real_time():
    """العودة للحاضر لجمع الهدايا بأمان"""
    print("⏪ [Time-Revert] Returning back 4 Hours to real-time...")
    now = datetime.datetime.utcnow()
    normal_time = now - datetime.timedelta(hours=4)
    
    success = set_system_time(normal_time)
    if not success:
        print("❌ ERROR: Failed to revert time back!")
        return False
    print("✅ SUCCESS: Time is back to normal. Safe to collect!")
    return True