"""
	Databridges Python server Library
	https://www.databridges.io/



	Copyright 2022 Optomate Technologies Private Limited.

	Licensed under the Apache License, Version 2.0 (the "License");
	you may not use this file except in compliance with the License.
	You may obtain a copy of the License at

	    http://www.apache.org/licenses/LICENSE-2.0

	Unless required by applicable law or agreed to in writing, software
	distributed under the License is distributed on an "AS IS" BASIS,
	WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
	See the License for the specific language governing permissions and
	limitations under the License.
"""

#version 20220419
errorLookup = {
    "E001": [1, 1],
    "E002": [1, 2],
    "E003": [1, 2],
    "E005": [1, 12],
    "E006": [1, 5],
    "E008": [1, 5],
    "E009": [1, 7],
    "E010": [1, 7],
    "E011": [4, 8],
    "E012": [5, 9],
    "E013": [5, 10],
    "E014": [6, 8],
    "E015": [6, 11],
    "E016": [6, 11],
    "E017": [6, 14],
    "E019": [19, 8],
    "E020": [19, 11],
    "E021": [19, 11],
    "E022": [19, 14],
    "E023": [19, 11],
    "E024": [11, 8],
    "E025": [11, 11],
    "E026": [11, 11],
    "E027": [11, 14],
    "E028": [11, 11],
    "E029": [11, 15],
    "E030": [12, 16],
    "E031": [12, 17],
    "E032": [12, 8],
    "E033": [20, 8],
    "E035": [20, 11],
    "E036": [20, 14],
    "E037": [20, 11],
    "E038": [20, 24],
    "E039": [20, 11],
    "E040": [3, 3],
    "E041": [10, 13],
    "E042": [20, 19],
    "E043": [25, 18],
    "E044": [25, 18],
    "E045": [25, 18],
    "E046": [25, 18],
    "E047": [26, 8],
    "E048": [21, 18],
    "E049": [21, 18],
    "E051": [21, 18],
    "E052": [21, 18],
    "E053": [21, 8],
    "E054": [15, 3],
    "E055": [22, 3],
    "E058": [6, 20],
    "E059": [6, 20],
    "E060": [1, 21],
    "E061": [24, 22],
    "E062": [24, 23],
    "E063": [1, 8],
    "E064": [7, 3],
    "E065": [14, 3],
    "E066": [16, 9],
    "E067": [16, 10],
    "E068": [27, 8],
    "E069": [27, 25],
    "E070": [13, 3],
    "E071": [2, 3],
    "E072": [26, 26],
    "E073": [26, 26],
    "E074": [17, 9],
    "E075": [17, 10],
    "E076": [18, 9],
    "E077": [18, 10],
    "E079": [15, 8],
    "E080": [15, 25],
    "E081": [8, 3],
    "E082": [9, 3],
    "E105": [27, 37],
    "E106": [23, 37],
    "E107": [27, 38],
    "E108": [23, 38],
    "E109": [20, 38],
    "E110": [32, 39],
    "E111": [32, 10],
    "E112": [33, 39],
    "E113": [33, 10]
}