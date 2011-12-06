cdef class Plottable(object):
    cdef public object viewport
    cdef public object x_interval
    cdef public object y_interval
    cdef public object dimensions
    
    cpdef resize(self, dimensions)
    cpdef plot(self, cr)
    cpdef plot_to_window(self, px=*, py=*)
    cpdef window_to_plot(self, wx=*, wy=*)
