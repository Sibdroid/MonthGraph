import typing as t
from datetime import datetime


class Month:

    def __init__(self,
                 month: t.Union[int, str],
                 year: int) -> None:
        """Initializes an object of type 'Month'.

        Args:
            month (t.Union[int, str]). Can be given in three ways:
                1) an int in [1, 12] range, where 1 is January
                   and 12 is December.
                2) a str representing a usual month name:
                   'January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October,' 'November' or
                   'December'.
                3) a str representing a shortened month name:
                   'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
                   'Sep', 'Sept', 'Oct', 'Nov' or 'Dec'. Note two versions
                   for September can be used interchangeably.
            year (int). An int in [0:99] or greater than or equal to 1000.
                Converted to2000+year in former case,
                parsed as is in latter case.
        Raises:
            ValueError: in three cases.
                1) If month is given as a str, but it is not one of the
                   supported month names.
                2) If month is given as an int, but it is outside [0; 11] range.
                3) If year is outside the [0: 99] range and is not greater than
                   or equal to 1000.
            TypeError:
                1) If month is not given as an int or a str.
                2) If year is not given as an int.
        """
        if isinstance(month, str):
            month_dict = {"January": 1,
                          "February": 2,
                          "March": 3,
                          "April": 4,
                          "May": 5,
                          "June": 6,
                          "July": 7,
                          "August": 8,
                          "September": 9,
                          "October": 10,
                          "November": 11,
                          "December": 12,
                          "Jan": 1,
                          "Feb": 2,
                          "Mar": 3,
                          "Apr": 4,
                          "Jun": 6,
                          "Jul": 7,
                          "Aug": 8,
                          "Sep": 9,
                          "Sept": 9,
                          "Oct": 10,
                          "Nov": 11,
                          "Dec": 12}
            month_names = [i for i in month_dict.keys()]
            try:
                self.month = month_dict[month]
            except KeyError:
                raise ValueError(
                    f"If given as a str, month has to be one of the "
                    f"following: \n{', '.join(month_names[:12])}\n"
                    f"{', '.join(month_names[-12:])}, not '{month}'")
        elif isinstance(month, int):
            if 1 <= month <= 12:
                self.month = month
            else:
                raise ValueError(
                    f"If given as an int, year has to be in [0, 11] interval"
                )
        else:
            raise TypeError(
                f"Month has to be given as a str or an int, "
                f"not {type(month)}"
            )
        if isinstance(year, int):
            if 0 <= year <= 99:
                self.year = 2000+year
            elif year >= 1000:
                self.year = year
            else:
                raise ValueError(
                    f"Year has to be either in [0, 99] range or greater "
                    f"than or equal to 1000, not {year}"
                )
        else:
            raise TypeError(
                f"Year has to be given as an int, "
                f"not {type(year)}"
            )
        self.starting_day = datetime.strptime(f"{self.year}-{self.month}",
                                              "%Y-%m").weekday()
        print(self.starting_day)


def main():
    month = Month(9, 2023)


if __name__ == "__main__":
    main()
