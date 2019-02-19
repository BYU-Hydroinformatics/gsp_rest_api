from main_controller import (get_forecast_streamflow_csv,
                             get_ecmwf_forecast_statistics,
                             get_forecast_ensemble_csv,
                             get_ecmwf_ensemble)
                            
from functions import get_units_title

from datetime import datetime as dt
from flask import jsonify, render_template, make_response

import logging


# create logger function
def init_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler('/app/api.log', 'a')
    formatter = logging.Formatter('%(asctime)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    

def forecast_stats_handler(request):
    """
    Controller that will retrieve forecast statistic data
    in different formats
    """
    
    init_logger()
    
    return_format = request.args.get('return_format', '')

    if (return_format == 'csv' or return_format == ''):
        csv_response = get_forecast_streamflow_csv(request)
        if (isinstance(csv_response, dict) and "error" in csv_response.keys()):
            return jsonify(csv_response)
        else:
            return csv_response
    
    elif (return_format == 'waterml' or return_format == 'json'):

        formatted_stat = {
            'high_res': 'High Resolution',
            'mean': 'Mean',
            'min': 'Min',
            'max': 'Max',
            'std_dev_range_lower': 'Standard Deviation Lower Range',
            'std_dev_range_upper': 'Standard Deviation Upper Range',
        }
    
        # retrieve statistics
        forecast_statistics, watershed_name, subbasin_name, river_id, units = \
            get_ecmwf_forecast_statistics(request)
    
        units_title = get_units_title(units)
        units_title_long = 'Meters'
        if units_title == 'ft':
            units_title_long = 'Feet'
    
        stat = request.args.get('stat', '')
    
        context = {
            'region': "-".join([watershed_name, subbasin_name]),
            'comid': river_id,
            'gendate': dt.utcnow().isoformat() + 'Z',
            'units': {
                'name': 'Streamflow',
                'short': '{}3/s'.format(units_title),
                'long': 'Cubic {} per Second'.format(units_title_long)
            }
        }
    
        stat_ts_dict = {}
        if (stat != '' and stat != 'all'):
    
            if stat not in formatted_stat.keys():
                logging.error('Invalid value for stat ...')
                return jsonify({"error": "Invalid value for stat parameter."})
                
            startdate = forecast_statistics[stat].index[0]\
                .strftime('%Y-%m-%dT%H:%M:%SZ')
            enddate = forecast_statistics[stat].index[-1]\
                .strftime('%Y-%m-%dT%H:%M:%SZ')
    
            time_series = []
            for date, value in forecast_statistics[stat].iteritems():
                time_series.append({
                    'date': date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'val': value
                })
    
            context['stats'] = {stat: formatted_stat[stat]}
            context['startdate'] = startdate
            context['enddate'] = enddate
            stat_ts_dict[stat] = time_series
            
        else:
            startdate = forecast_statistics['mean'].index[0]\
                .strftime('%Y-%m-%dT%H:%M:%SZ')
            enddate = forecast_statistics['mean'].index[-1]\
                .strftime('%Y-%m-%dT%H:%M:%SZ')
            
            high_r_time_series = []
            for date, value in forecast_statistics['high_res'].iteritems():
                high_r_time_series.append({
                    'date': date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'val': value
                })
            
            mean_time_series = []
            for date, value in forecast_statistics['mean'].iteritems():
                mean_time_series.append({
                    'date': date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'val': value
                })
                
            max_time_series = []
            for date, value in forecast_statistics['max'].iteritems():
                max_time_series.append({
                    'date': date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'val': value
                })
                
            min_time_series = []
            for date, value in forecast_statistics['min'].iteritems():
                min_time_series.append({
                    'date': date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'val': value
                })
                
            std_d_lower_time_series = []
            for date, value in forecast_statistics['std_dev_range_lower'].iteritems():
                std_d_lower_time_series.append({
                    'date': date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'val': value
                })
                
            std_d_upper_time_series = []
            for date, value in forecast_statistics['std_dev_range_upper'].iteritems():
                std_d_upper_time_series.append({
                    'date': date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'val': value
                })
                
            context['stats'] = formatted_stat
            
            context['startdate'] = startdate
            context['enddate'] = enddate
            stat_ts_dict['high_res'] = high_r_time_series
            stat_ts_dict['mean'] = mean_time_series
            stat_ts_dict['max'] = max_time_series
            stat_ts_dict['min'] = min_time_series
            stat_ts_dict['std_dev_range_lower'] = std_d_lower_time_series
            stat_ts_dict['std_dev_range_upper'] = std_d_upper_time_series
            
        context['time_series'] = stat_ts_dict
            
    
        if return_format == "waterml":
            xml_response = \
                make_response(render_template('forecast_stats.xml', **context))
            xml_response.headers.set('Content-Type', 'application/xml')
        
            return xml_response
        
        if return_format == "json":
            return jsonify(context)
        
    else:
        return jsonify({"error": "Invalid return_format."})


def forecast_ensembles_handler(request):
    """
    Controller that will retrieve forecast ensemble data
    in different formats
    """
    
    init_logger()
    
    return_format = request.args.get('return_format', '')

    if (return_format == 'csv' or return_format == ''):
        csv_response = get_forecast_ensemble_csv(request)
        if (isinstance(csv_response, dict) and "error" in csv_response.keys()):
            return jsonify(csv_response)
        else:
            return csv_response
    
    elif (return_format == 'waterml' or return_format == 'json'):
    
        # retrieve statistics
        forecast_statistics, watershed_name, subbasin_name, river_id, units = \
            get_ecmwf_ensemble(request)

        formatted_ensemble = {}
        for ens in sorted(forecast_statistics.key()):
            formatted_ensemble[ens.split('_')[1]] = ens.title().replace('_', ' ')

        units_title = get_units_title(units)
        units_title_long = 'Meters'
        if units_title == 'ft':
            units_title_long = 'Feet'
    
        ensemble = request.args.get('ensemble', '')
    
        context = {
            'region': "-".join([watershed_name, subbasin_name]),
            'comid': river_id,
            'gendate': dt.utcnow().isoformat() + 'Z',
            'units': {
                'name': 'Streamflow',
                'short': '{}3/s'.format(units_title),
                'long': 'Cubic {} per Second'.format(units_title_long)
            }
        }
    
        stat_ts_dict = {}
        if (ensemble != '' and ensemble != 'all' and '-' not in ensemble and ',' not in ensemble):
    
            if int(ensemble) not in map(int, sorted(formatted_ensemble.keys())):
                logging.error('Invalid value for ensemble ...')
                return jsonify({"error": "Invalid value for ensemble parameter."})
                
            startdate = forecast_statistics['{0:02}'.format(ensemble)].index[0]\
                .strftime('%Y-%m-%dT%H:%M:%SZ')
            enddate = forecast_statistics['{0:02}'.format(ensemble)].index[-1]\
                .strftime('%Y-%m-%dT%H:%M:%SZ')
    
            time_series = []
            for date, value in forecast_statistics['ensemble_{0:02}'.format(ensemble)].iteritems():
                time_series.append({
                    'date': date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'val': value
                })
    
            context['ensembles'] = {'{0:02}'.format(ensemble): formatted_ensemble['ensemble_{0:02}'.format(ensemble)]}
            context['startdate'] = startdate
            context['enddate'] = enddate
            stat_ts_dict['{0:02}'.format(ensemble)] = time_series
            
        else:
            startdate = forecast_statistics['ensemble_01'].index[0]\
                .strftime('%Y-%m-%dT%H:%M:%SZ')
            enddate = forecast_statistics['ensemble_01'].index[-1]\
                .strftime('%Y-%m-%dT%H:%M:%SZ')
            
            high_r_time_series = []
            for date, value in forecast_statistics['high_res'].iteritems():
                high_r_time_series.append({
                    'date': date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'val': value
                })
            
            mean_time_series = []
            for date, value in forecast_statistics['mean'].iteritems():
                mean_time_series.append({
                    'date': date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'val': value
                })
                
            max_time_series = []
            for date, value in forecast_statistics['max'].iteritems():
                max_time_series.append({
                    'date': date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'val': value
                })
                
            min_time_series = []
            for date, value in forecast_statistics['min'].iteritems():
                min_time_series.append({
                    'date': date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'val': value
                })
                
            std_d_lower_time_series = []
            for date, value in forecast_statistics['std_dev_range_lower'].iteritems():
                std_d_lower_time_series.append({
                    'date': date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'val': value
                })
                
            std_d_upper_time_series = []
            for date, value in forecast_statistics['std_dev_range_upper'].iteritems():
                std_d_upper_time_series.append({
                    'date': date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'val': value
                })
                
            context['stats'] = formatted_stat
            
            context['startdate'] = startdate
            context['enddate'] = enddate
            stat_ts_dict['high_res'] = high_r_time_series
            stat_ts_dict['mean'] = mean_time_series
            stat_ts_dict['max'] = max_time_series
            stat_ts_dict['min'] = min_time_series
            stat_ts_dict['std_dev_range_lower'] = std_d_lower_time_series
            stat_ts_dict['std_dev_range_upper'] = std_d_upper_time_series
            
        context['time_series'] = stat_ts_dict
            
    
        if return_format == "waterml":
            xml_response = \
                make_response(render_template('forecast_stats.xml', **context))
            xml_response.headers.set('Content-Type', 'application/xml')
        
            return xml_response
        
        if return_format == "json":
            return jsonify(context)
        
    else:
        return jsonify({"error": "Invalid return_format."})