__author__ = 'laurens'


# check: http://www.highcharts.com/demo


UNDEFINED = 'UD'

POINT = 'P'
SQUARE = 'S'
TRIANGLE = 'T'

DATA_POINT_TYPES = (
    (UNDEFINED, 'undefined'),
    (POINT, 'undefined'),
    (SQUARE, 'undefined'),
    (TRIANGLE, 'undefined'),
)


CLICK_POINTS = 'CP'
CLICK_SQUARES = 'CS'
CLICK_TRIANGLES = 'CT'
LABELED_POINTS = 'LP'
LABELED_SQUARES = 'LS'
LABELED_TRIANGLES = 'LT'
ERROR_BAR = 'EB'
POLYGON_AREA = 'PA'

DATA_GROUP_TYPES = (
    (UNDEFINED, 'undefined'),
    (CLICK_POINTS, 'undefined'),
    (CLICK_SQUARES, 'undefined'),
    (CLICK_TRIANGLES, 'undefined'),
    (LABELED_POINTS, 'undefined'),
    (LABELED_SQUARES, 'undefined'),
    (LABELED_TRIANGLES, 'undefined'),
    (ERROR_BAR, 'undefined'),
    (POLYGON_AREA, 'undefined'),
)

X_AX = 'X'
Y_AX = 'Y'
Z_AX = 'Z'

AX_LABEL_TYPES = (
    (X_AX, 'x_ax'),
    (Y_AX, 'y_ax'),
    (Z_AX, 'z_ax'),
)


BASIC_GRAPH = 'BLH'
BASIC_GRAPH_LOG_AXIS_Y = 'BLY'
BASIC_GRAPH_LOG_AXIS_X = 'BLX'
BASIC_GRAPH_LOG_AXIS_XY = 'BXY'
BASIC_GRAPH_AREA = 'BLA'
STACKED_AREA = 'SAA'
PERCENTAGE_AREA = 'PAA'
AREA_RANGE = 'ARE'
BASIC_BAR = 'BBR'
STACKED_BAR = 'SBR'
NEGATIVE_STACK_BAR = 'NSB'
BASIC_COLUMN = 'BCN'
STACKED_COLUMN = 'SCN'
NEGATIVE_COLUMN = 'NCN'
COLUMN_RANGE = 'CRE'
PEI_CHART = 'PCH'
DONUT_CHART = 'DCT'
SCATTER_PLOT = 'SPT'
BUBBLE_CHART = 'BCH'
SCATTER_CHART_3D = 'SC3'
COLUMN_3D = 'C3D'
PEI_3D = 'P3D'
DONUT_3D = 'D3D'
HEAT_MAP = 'HMP'
POLAR_CHART = 'POC'
BOX_PLOT = 'BPT'
WATERFALL = 'WFL'
COLUMN_ERROR_BAR = 'CEB'
POLYGON_SERIES = 'PSE'

DATA_VIEW_TYPES = (
    (UNDEFINED, 'undefined'),
    (BASIC_GRAPH, 'undefined'),
    (BASIC_GRAPH_LOG_AXIS_Y, 'undefined'),
    (BASIC_GRAPH_LOG_AXIS_X, 'undefined'),
    (BASIC_GRAPH_LOG_AXIS_XY, 'undefined'),
    (BASIC_GRAPH_AREA, 'undefined'),
    (STACKED_AREA, 'undefined'),
    (PERCENTAGE_AREA, 'undefined'),
    (AREA_RANGE, 'undefined'),
    (BASIC_BAR, 'undefined'),
    (STACKED_BAR, 'undefined'),
    (NEGATIVE_STACK_BAR, 'undefined'),
    (BASIC_COLUMN, 'undefined'),
    (STACKED_COLUMN, 'undefined'),
    (NEGATIVE_COLUMN, 'undefined'),
    (COLUMN_RANGE, 'undefined'),
    (PEI_CHART, 'undefined'),
    (DONUT_CHART, 'undefined'),
    (SCATTER_PLOT, 'undefined'),
    (BUBBLE_CHART, 'undefined'),
    (SCATTER_CHART_3D, 'undefined'),
    (COLUMN_3D, 'undefined'),
    (PEI_3D, 'undefined'),
    (DONUT_3D, 'undefined'),
    (HEAT_MAP, 'undefined'),
    (POLAR_CHART, 'undefined'),
    (BOX_PLOT, 'undefined'),
    (WATERFALL, 'undefined'),
    (COLUMN_ERROR_BAR, 'undefined'),
    (POLYGON_SERIES, 'undefined'),
)