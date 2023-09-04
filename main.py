import typing as t
import warnings
import calendar
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


def get_colors_and_values(data: t.Union[pd.DataFrame, None],
                          colors: t.Union[list[str], None],
                          values: t.Union[list[float], None]):
    if isinstance(data, pd.DataFrame):
        if "colors" in data.columns:
            return data["colors"].tolist(), None
        elif "values" in data.columns:
            return None, data["values"].tolist()
    if isinstance(colors, list):
        return colors, None
    if isinstance(values, list):
        return None, values
    return None, None


class Month:

    def __init__(self,
                 month: t.Union[int, str],
                 year: int,
                 data: t.Union[pd.DataFrame, None]=None,
                 colors: t.Union[list[str], None]=None,
                 values: t.Union[list[float], None]=None,
                 colormap: str = "viridis",
                 neutral_color: str="#EEEEEE") -> None:
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
            colors (str). A list of colors, each represented as a hex value.
            neutral_color (str). The color used for days outside the month.
        Raises:
            ValueError: in four cases.
                1) If month is given as a str, but it is not one of the
                   supported month names.
                2) If month is given as an int, but it is outside [0; 11] range.
                3) If year is outside the [0: 99] range and is not greater than
                   or equal to 1000.
                4) If the amount of colors is not equal to the amount of
                   days in the month.
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
                self._month = month_dict[month]
            except KeyError:
                raise ValueError(
                    f"If given as a str, month has to be one of the "
                    f"following: \n{', '.join(month_names[:12])}\n"
                    f"{', '.join(month_names[-12:])}, not '{month}'")
        elif isinstance(month, int):
            if 1 <= month <= 12:
                self._month = month
            else:
                raise ValueError(
                    f"If given as an int, year has to be in [0, 11] interval"
                )
        else:
            raise TypeError(
                f"month has to be given as a str or an int, "
                f"not {type(month)}"
            )
        if isinstance(year, int):
            if 0 <= year <= 99:
                self._year = 2000+year
            elif year >= 1000:
                self._year = year
            else:
                raise ValueError(
                    f"year has to be either in [0, 99] range or greater "
                    f"than or equal to 1000, not {year}"
                )
        else:
            raise TypeError(
                f"year has to be given as an int, "
                f"not {type(year)}"
            )
        self._starting_day, self._day_count = calendar.monthrange(self._year,
                                                                  self._month)
        self._colors, self._values = get_colors_and_values(data, colors, values)
        if self._colors is None and self._values is None:
            raise ValueError(
                "Neither colors nor values found: please, provide them as "
                "columns of 'data' or separate respective arguments"
            )
        self._colormap = colormap
        self._neutral_color = neutral_color
        self._image = None
        self._draw = None
        if self._colors is None:
            self._values_to_colors()
        print(self._colors)
        self._set_canvas()
        #self._paint()
        #self._add_text()
        #self._save()

    def _values_to_colors(self):
        self._colors = []
        slope = 1/(max(self._values)-min(self._values))
        for value in self._values:
            self._colors += [slope*(value-min(self._values))]

    def _set_canvas(self):
        self._image = Image.new("RGB", (780, 720), (255, 255, 255))
        self._draw = ImageDraw.Draw(self._image)

    def _paint(self):
        coordinates = [10, 60]
        count = 0
        for color in self._colors:
            if color is not None:
                self._draw.rectangle((coordinates[0], coordinates[1],
                                      coordinates[0]+100, coordinates[1]+100),
                                     fill=color)
            else:
                self._draw.rectangle((coordinates[0], coordinates[1],
                                      coordinates[0] + 100,
                                      coordinates[1] + 100),
                                     fill=self._neutral_color)
            coordinates[0] += 110
            count += 1
            if count == 7:
                coordinates[0] = 10
                coordinates[1] += 110
                count = 0

    def _add_text(self):
        font = ImageFont.truetype("Roboto-Thin.ttf", 30)
        days = ["Mon.", "Tue.", "Wed.", "Thu.", "Fri.", "Sat.", "Sun."]
        x_coordinates = [25, 140, 250, 360, 480, 585, 690]
        for day, x_coordinate in zip(days, x_coordinates):
            self._draw.text((x_coordinate, 15),
                            day, "black", font=font)

    def _save(self):
        self._image.save("test.png")


def main():
    df = pd.DataFrame({"values": [1, 2, 3]})
    month = Month(9, 2023, df)


if __name__ == "__main__":
    main()
