from datetime import datetime as dt
"""python script for getting input in YYYY-MM-DD format"""
class EndBeforeStartException(Exception):
    "Raised when start date is after end"
    pass
class FutureException(Exception):
    "Raised when end is past current date"
def get_valid_date_range():
    while True:
        try:
            val = input('input a valid date range YYYY-MM-DD YYYY-MM-DD: ')
            start = val[:10].strip()
            end = val[10:].strip()
            startDate = dt.strptime(start, "%Y-%m-%d")
            endDate = dt.strptime(end, "%Y-%m-%d")
            if startDate >= endDate:
                raise EndBeforeStartException
            if endDate > dt.today():
                raise FutureException
            return startDate, endDate
        except EndBeforeStartException:
            print("End cannot come before start")
        except FutureException:
            print('end cannot be past current date')
        except:
            print('please enter start and end dates in correct format')
        
if __name__ == "__main__":
    startDate, endDate = get_valid_date_range()

