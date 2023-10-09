import typing as t
import os
import calendar
import matplotlib as mpl
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageColor
from random import randint
from pprint import pformat
MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]

def get_colors_and_values(data: t.Union[pd.DataFrame, None],
                          colors: t.Union[list[str], None],
                          values: t.Union[list[float], None]
                          ) -> tuple[t.Union[list, None], t.Union[list, None]]:
    """Accesses colors and values from a DataFrame or respective arguments.

    Args:
        data (pd.DataFrame | None). May or may not contain 'colors'
            and 'values' arguments.
        colors (list[str] | None).
        values (list[float] | None).

    Returns:
        A tuple of colors (list[str] | None) and values (list[str] | None).
    """
    new_colors = None
    new_values = None
    if isinstance(data, pd.DataFrame):
        if "colors" in data.columns:
            new_colors = data["colors"].tolist()
        elif "values" in data.columns:
            new_values = data["values"].tolist()
    if isinstance(colors, list) and new_colors is None:
        new_colors = colors
    if isinstance(values, list) and new_values is None:
        new_values = values
    return new_colors, new_values


def background_to_color(color: t.Union[tuple[int, int, int], str]
                        ) -> t.Literal["#000000", "#ffffff"]:
    """Returns the text color (black or white) based on the background color.

    Args:
        color (tuple[int, int, int] | str): the color. If given as a tuple
            of ints, they should be in [0, 255] range.

    Returns:
        '#000000' (black) or '#ffffff' (white).
    """
    if isinstance(color, str):
        color = ImageColor.getcolor(color, "RGB")
    red, green, blue = color
    if red*0.299 + green*0.587 + blue*0.114 > 186:
        return "#000000"
    return "#ffffff"


def get_text_dimensions(font: ImageFont.FreeTypeFont,
                        text: str) -> tuple[float, float]:
    """Calculates text's width and height given a font.

    Args:
        font (ImageFont.FreeTypeFont).
        text (str).

    Returns:
        The width and height of the text.
    """
    ascent, descent = font.getmetrics()
    width = font.getmask(text).getbbox()[2]
    height = font.getmask(text).getbbox()[3] + descent
    return width, height


def get_text_coordinates(text_width: float,
                         text_height: float,
                         box_x: int,
                         box_y: int,
                         box_width: int,
                         box_height: int) -> tuple[float, float]:
    """Calculates the text's coordinates to fit in the centre of the box.

    Args:
        text_width (float).
        text_height (float).
        box_x (int): the starting x-coordinate of the box.
        box_y (int): the starting y-coordinate of the box.
        box_width (int).
        box_height (int).

    Returns:
        The required coordinates (top-left corner) of the text.
    """
    return (box_x+(box_width-text_width)/2,
            box_y+(box_height-text_height)/2)

class Month:

    def __init__(self,
                 month: t.Union[int, str],
                 year: int,
                 data: t.Optional[pd.DataFrame] = None,
                 colors: t.Optional[list[str]] = None,
                 values: t.Optional[list[float]] = None,
                 colormap: str = "viridis",
                 font: str = "Roboto-Thin",
                 text_color: str = "#000000",
                 background_color: str = "#FFFFFF",
                 neutral_color: str = "#EEEEEE",
                 first_day: str = "Monday",
                 show_annotation: bool = True,
                 annotation_precision: int = 2) -> None:
        """Initializes an object of type 'Month'.

        Args:
            month (int | str). Can be given in three ways:
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
                Converted to 2000+year in former case,
                parsed as-is in latter case.
            data (pd.DataFrame | None). Either a DataFrame that preferably
                has either of the two columns: 'colors' and 'values' (or both),
                or None. Defaults to None. If provided, 'colors' and 'values'
                take precedence over the respective arguments.
            colors (str | None). A list of colors,
                each represented as a hex value, or None. Defaults to None.
            values (float | None). A list of values, or None. Defaults to None.
            colormap (str). A colormap used to convert values to colors.
                Does not matter if the colors are already provided.
                Defaults to 'viridis'.
            font (str). The name of the font used for the text.
                Defaults to 'Roboto-Thin'.
            neutral_color (str). The color used for days outside the month.
                Defaults to '#EEEEEE', that is, a light gray.
            first_day (str). The first day of the month, can be one of the:
                * 'Monday', 'Mon', 'Mon.'
                * 'Sunday', 'Sun', 'Sun.'
                * 'Saturday', 'Sat', 'Sat.'
                * 'Friday', 'Fri', 'Fri.'
                Defaults to 'Monday'.
            show_annotation (bool). Whether to draw the annotation for the
                cells. Defaults to True.
            annotation_precision (int). Defaults to 2.
        Raises:
            ValueError: in eight cases.
                1) If month is given as a str, but it is not one of the
                   supported month names.
                2) If month is given as an int, but it is outside [0; 11] range.
                3) If year is outside the [0: 99] range and is not greater than
                   or equal to 1000.
                4) If neither colors nor values have been found in either
                   data or respective arguments.
                5) If the colormap provided is not supported.
                6) If the font provided is not supported.
                7) If the amount of colors is not equal to the amount of
                   days in the month.
                8) If the first day of week provided is not supported.
            TypeError: in two cases.
                1) If month is not given as an int or a str.
                2) If year is not given as an int.
        """
        self._locals = locals()
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
                self._year = 2000 + year
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
        if first_day in ["Monday", "Mon", "Mon."]:
            self._days = ["Mon.", "Tue.", "Wed.",
                          "Thu.", "Fri.", "Sat.", "Sun."]
        elif first_day in ["Sunday", "Sun", "Sun."]:
            self._starting_day += 1
            self._days = ["Sun.", "Mon.", "Tue.",
                          "Wed.", "Thu.", "Fri.", "Sat."]
        elif first_day in ["Saturday", "Sat", "Sat."]:
            self._starting_day += 2
            self._days = ["Sat.", "Sun.", "Mon.",
                          "Tue.", "Wed.", "Thu.", "Fri."]
        elif first_day in ["Friday", "Fri", "Fri."]:
            self._starting_day += 3
            self._days = ["Fri.", "Sat.", "Sun.",
                          "Mon.", "Tue.", "Wed.", "Thu."]
        else:
            raise ValueError(
                f"first_day has to be one of the following values"
                f"\n* 'Monday', 'Mon', 'Mon.',"
                f"\n* 'Sunday', 'Sun', 'Sun.',"
                f"\n* 'Saturday', 'Sat', 'Sat.',"
                f"\n* 'Friday', 'Fri', 'Fri.', not '{first_day}'"
            )
        self._show_annotation = show_annotation
        self._annotation_precision = annotation_precision
        self._colors, self._values = get_colors_and_values(data, colors, values)
        if self._colors is None and self._values is None:
            raise ValueError(
                "Neither colors nor values found: please, provide them as "
                "columns of 'data' or separate respective arguments"
            )
        try:
            self._colormap = mpl.colormaps[colormap]
        except KeyError:
            raise ValueError(
                f"'{colormap}' is not a supported colormap"
            )
        if os.path.exists(f"fonts/{font}.ttf"):
            self._font_path = f"fonts/{font}.ttf"
        else:
            raise ValueError(f"{font} is not a supported font")
        self._text_color = text_color
        self._background_color = background_color
        self._neutral_color = neutral_color
        self._image = None
        self._draw = None
        if self._colors is None:
            self._values_to_colors()
        if len(self._colors) == self._day_count:
            self._colors = [None] * self._starting_day + self._colors
            self._colors += [None] * (42 - len(self._colors))
            if self._values is not None:
                self._values = [None] * self._starting_day + self._values
                self._values += [None] * (42 - len(self._values))
            if all([i is None for i in self._colors[:7]]):
                self._colors = self._colors[7:] + [None] * 7
                self._values = self._values[7:] + [None] * 7
        else:
            raise ValueError(
                f"The amount of colors ({len(self._colors)}) "
                f"has to be equal to the amount of days ({self._day_count})"
            )
        self._set_canvas()
        self._paint()
        if self._values is not None and self._show_annotation:
            self._add_text_annotation()
        self._add_text_months()
        self._add_text_title()
        self._save()


    def _values_to_colors(self):
        self._colors = []
        slope = 1 / (max(self._values) - min(self._values))
        for value in self._values:
            if pd.isna(value):
                self._colors += [None]
            else:
                ranged_value = slope * (value - min(self._values))
                color = self._colormap(ranged_value)
                color = tuple([int(round(i * 255, 0)) for
                               i in list(color)[:-1]])
                self._colors += [color]

    def _set_canvas(self):
        self._image = Image.new("RGB", (780, 800), self._background_color)
        self._draw = ImageDraw.Draw(self._image)

    def _paint(self):
        coordinates = [10, 140]
        count = 0
        for color in self._colors:
            if color is not None:
                self._draw.rectangle((coordinates[0], coordinates[1],
                                      coordinates[0] + 100,
                                      coordinates[1] + 100),
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

    def _add_text_annotation(self):
        font = ImageFont.truetype(self._font_path, 30)
        coordinates = [10, 140]
        count = 0
        for value, color in zip(self._values, self._colors):
            if not pd.isna(value):
                if value == int(value):
                    annot_value = f"{int(value)}"
                else:
                    annot_value = f"{round(value, self._annotation_precision)}"
                width, height = get_text_dimensions(font, annot_value)
                new_coordinates = get_text_coordinates(width, height,
                                                       coordinates[0],
                                                       coordinates[1],
                                                       100, 100)
                self._draw.text((int(new_coordinates[0]),
                                 int(new_coordinates[1])),
                                annot_value, background_to_color(color),
                                font=font)
            coordinates[0] += 110
            count += 1
            if count == 7:
                coordinates[0] = 10
                coordinates[1] += 110
                count = 0

    def _add_text_months(self):
        font = ImageFont.truetype(self._font_path, 30)
        x_coordinates = [25, 140, 250, 360, 480, 585, 690]
        for day, x_coordinate in zip(self._days, x_coordinates):
            self._draw.text((x_coordinate, 95),
                            day, font=font, fill=self._text_color)

    def _add_text_title(self):
        font = ImageFont.truetype(self._font_path, 45)
        month = MONTHS[self._month-1]
        title = f"{month} {self._year}"
        self._draw.text((300-10*(len(month)-3), 25), title, font=font,
                        fill=self._text_color)

    def _save(self):
        self._image.save(f"test.png")

    def __repr__(self):
        string = "Month("
        for argument in self._locals:
            if argument != "self":
                value = self._locals[argument]
                if isinstance(value, pd.DataFrame):
                    header = f"pd.DataFrame("
                    for j in value.columns:
                        header += f"{{'{j}': {value[j].tolist()}}})"
                elif isinstance(value, str):
                    header = f"'{value}'"
                else:
                    header = value
                line = f"{argument} = {header}, "
                if len(string.splitlines()[-1] + line) >= 80:
                    string += "\n"
                string += line
        # remove the last space and comma pair
        string = string[:-2]
        return string + ")"



def main():
    values = [randint(1, 10000) / 100 for _ in range(30)]
    values[12] = None
    df = pd.DataFrame({"values": values})
    month = Month(9, 2023, df, colormap="viridis", font="Roboto",
                  text_color="#EEEEEE",
                  background_color="black",
                  neutral_color="#222222", annotation_precision=3)
    print(month)


if __name__ == "__main__":
    main()
