import os
import tempfile

os.environ['MPLBACKEND'] = 'Agg'
os.environ.setdefault('MPLCONFIGDIR', tempfile.mkdtemp(prefix='scanplot-mpl-'))
