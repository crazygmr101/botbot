"""
Copyright 2021 crazygmr101

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the 
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit 
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the 
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE 
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from typing import TypeVar, Callable, List, Optional, Union

_T = TypeVar("_T")
_S = TypeVar("_S")


def binary_search(lst: List[_T], search_for: _S, search_predicate: Optional[Callable[[_T], _S]] = None, low: int = None,
                  high: int = None):
    print(search_for)
    print(list(map(search_predicate, lst)))
    low = low or 0
    high = high or len(lst) - 1
    search_predicate = search_predicate or (lambda x: x)
    if high >= low:
        mid = (high + low) // 2
        if search_predicate(lst[mid]) == search_for:
            return mid
        elif search_predicate(lst[mid]) > search_for:
            return binary_search(lst, search_for, search_predicate, low, mid - 1)
        else:
            return binary_search(lst, search_for, search_predicate, mid + 1, high)
    else:
        raise ValueError


class Null:
    @classmethod
    def safe(cls, var: _T) -> Union["Null", _T]:
        return var or cls()

    def __call__(self, *args, **kwargs):
        return

    def __getattr__(self, item):
        return self.__class__()
