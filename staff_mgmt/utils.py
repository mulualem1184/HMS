# utility functions and classes
import random

class TimeOverlapError(Exception):
    pass


def get_minutes(t):
    return t.hour*60 + t.minute


def get_time_difference(t1, t2):
    # returns t2 - t1 in minutes
    return (t2.hour*60 + t2.minute) - (t1.hour*60 + t1.minute)

def check_time_overlap(first_interval:tuple, second_interval:tuple, offset_min=1) -> bool:
    t1, t2 = [get_minutes(x) for x in first_interval]
    t3, t4 = [get_minutes(x) for x in second_interval]
    print(f"t1, t2 is {t1}, {t2}")
    print(f"t3, t4 is {t3}, {t4}")
    if (t3 == t2):
        return False
    if (t3 > t1) and (t3 < t2):
        return True
    if (t4 >= t1) and (t4 <= t2):
        return True
    return False


def generate_random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 120)
    b = random.randint(0, 255)
    return f'rgb({r},{g},{b})'


def save_permission_form(self,form, designation,model_str):

    form1 = form.save(commit=False)
    try:
        if model_str == 'M':
            obj = designation.permission.medical
        elif model_str == 'C':
            obj = designation.permission.component
            for f in form.changed_data:
                try:
                    print(self.request.POST[f],'\n')
                    if self.request.POST[f] == 'on':
                        value = True
                except Exception as e:
                    value = False
                setattr(obj,f,value)                
                print('has reached')

            obj.save()
            messages.success(self.request, "Permission Given successfully!")
            return redirect('staff:assign_previlages', designation.id)
        
    except Exception as e:
        obj.save()
        messages.success(self.request, "Permission Given successfully!")
        return redirect('staff:assign_previlages', designation.id)
