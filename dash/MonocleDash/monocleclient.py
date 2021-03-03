import json
import urllib.parse
import urllib.request
import DataSources.monocledb


class MonocleData:
   """ provides wrapper for classes that query various data sources for Monocle data """
   
   def __init__(self):
      self.monocledb = DataSources.monocledb.MonocleDB()

   def get_progress(self):
      return self.mock_progress

   def get_institutions(self):
      names = self.monocledb.get_institution_names()
      institutions = {}
      for this_name in names:
         key = self.institution_name_to_key(this_name, institutions.keys())
         institutions[key] = this_name
      return institutions
   
   def get_batches(self, institutions):
      batches = {}
      i = 0
      for this_institution in sorted( institutions.keys(), key=institutions.__getitem__ ):
         batches[this_institution] = self.mock_batches[ i % len(self.mock_batches) ]
         i += 1
      return batches
   
   def get_sequencing_status(self, institutions):
      sequencing_status = {}
      i = 0
      for this_institution in sorted( institutions.keys(), key=institutions.__getitem__ ):
         sequencing_status[this_institution] = self.mock_sequencing_status[ i % len(self.mock_sequencing_status) ]
         i += 1
      return sequencing_status
   
   def get_pipeline_status(self, institutions):
      pipeline_status = {}
      i = 0
      for this_institution in sorted( institutions.keys(), key=institutions.__getitem__ ):
         pipeline_status[this_institution] = self.mock_pipeline_status[ i % len(self.mock_pipeline_status) ]
         i += 1
      return pipeline_status

   def institution_name_to_key(self, name, existing_keys):
      # create key from institution name -- shortened, no non-alphanumerics
      key = ''
      for word in name.split():
         if word[0].isupper():
            key += word[0:3]
         if 12 < len(key):
            break
      # almost certain to be unique, but...
      while key in existing_keys:
         key += '_X'
      return(key)


   mock_progress = { 'months'             : [1,2,3,4,5,6,7,8,9],
                     'samples received'   : [158,225,367,420,580,690,750,835,954],
                     'samples sequenced'  : [95,185,294,399,503,640,730,804,895],
                     }

   mock_batches = [  {  'expected'  : 800,
                        'received'  : 188,
                        'deliveries': [{'name': 'batch 1', 'date': '3 Dec 2020',  'number': 95  },
                                       {'name': 'batch 2', 'date': '11 Jan 2021', 'number': 93  },
                                       ]
                        },
                     {  'expected'  : 1200,
                        'received'  : 668,
                        'deliveries': [{'name': 'batch 1', 'date': '24 Nov 2020', 'number': 237 },
                                       {'name': 'batch 2', 'date': '16 Dec 2020', 'number': 175 },
                                       {'name': 'batch 3', 'date': '3 Jan 2021',  'number': 194 },
                                       ]
                        },
                     {  'expected'  : 900,
                        'received'  : 232,
                        'deliveries': [{'name': 'batch 1', 'date': '28 Dec 2020', 'number': 104 },
                                       {'name': 'batch 2', 'date': '27 Jan 2021', 'number': 128 },
                                       ]
                        },
                     {  'expected'  : 1500,
                        'received'  : 341,
                        'deliveries': [{'name': 'batch 1', 'date': '25 Feb 2021', 'number': 341 },
                                       ]
                        },
                     {  'expected'  : 1000,
                        'received'  : 505,
                        'deliveries': [{'name': 'batch 1', 'date': '30 Oct 2020', 'number': 76  },
                                       {'name': 'batch 2', 'date': '24 Nov 2020', 'number': 85  },
                                       {'name': 'batch 3', 'date': '17 Dec 2020', 'number': 105 },
                                       {'name': 'batch 4', 'date': '11 Jan 2021', 'number': 128 },
                                       {'name': 'batch 5', 'date': '3 Feb 2021',  'number': 111 },
                                       ]
                        },
                     {  'expected'  : 600,
                        'received'  : 203,
                        'deliveries': [{'name': 'batch 1', 'date': '17 Jan 2020', 'number': 203 },
                                       ]
                        },
                     ]
   
   mock_sequencing_status = [ {  'received'  : mock_batches[0]['received'],
                                 'completed' : 173,
                                 'failed'    : []
                                 },
                              {  'received'  : mock_batches[1]['received'],
                                 'completed' : 632,
                                 'failed'    : [{  'sample' : '4321STDY4321099',
                                                   'qc'     : 'DNA',
                                                   'issue'  : 'DNA concentration 7nM  required >= 10nM',
                                                   },
                                                {  'sample' : '4321STDY4334078',
                                                   'qc'     : 'sequencing',
                                                   'issue'  : 'Phred scores across sequences are insufficient quality',
                                                   },
                                                {  'sample' : '4321STDY4321099',
                                                   'qc'     : 'DNA',
                                                   'issue'  : 'DNA concentration 7nM  required >= 10nM',
                                                   },
                                                {  'sample' : '4321STDY4334078',
                                                   'qc'     : 'sequencing',
                                                   'issue'  : 'Phred scores across sequences are insufficient quality',
                                                   },
                                                ]
                                 },
                              {  'received'  : mock_batches[2]['received'],
                                 'completed' : 198,
                                 'failed'    : []
                                 },
                              {  'received'  : mock_batches[3]['received'],
                                 'completed' : 0,
                                 'failed'    : []
                                 },
                              {  'received'  : mock_batches[4]['received'],
                                 'completed' : 394,
                                 'failed'    : [{  'sample' : '4321STDY4321099',
                                                   'qc'     : 'DNA',
                                                   'issue'  : 'DNA concentration 7nM  required >= 10nM',
                                                   },
                                                {  'sample' : '4321STDY4334078',
                                                   'qc'     : 'sequencing',
                                                   'issue'  : 'Phred scores across sequences are insufficient quality',
                                                   },
                                                {  'sample' : '4321STDY4321099',
                                                   'qc'     : 'DNA',
                                                   'issue'  : 'DNA concentration 7nM  required >= 10nM',
                                                   },
                                                ]
                                 },
                              {  'received'  : mock_batches[5]['received'],
                                 'completed' : 157,
                                 'failed'    : [{  'sample' : '4321STDY4321099',
                                                   'qc'     : 'DNA',
                                                   'issue'  : 'DNA concentration 7nM  required >= 10nM',
                                                   },
                                                {  'sample' : '4321STDY4334078',
                                                   'qc'     : 'sequencing',
                                                   'issue'  : 'Phred scores across sequences are insufficient quality',
                                                   },
                                                ]
                                 },
                              ]

   mock_pipeline_status = [   {  'sequenced' : mock_sequencing_status[0]['completed']-len(mock_sequencing_status[0]['failed']),
                                 'running'   : 30,
                                 'completed' : 63,
                                 'failed'    : []
                                 },
                              {  'sequenced' : mock_sequencing_status[1]['completed']-len(mock_sequencing_status[1]['failed']),
                                 'running'   : 180,
                                 'completed' : 187,
                                 'failed'    : [{  'sample' : '4321STDY4321099',
                                                   'qc'     : 'DNA',
                                                   'issue'  : 'DNA concentration 7nM  required >= 10nM',
                                                   },
                                                {  'sample' : '4321STDY4334078',
                                                   'qc'     : 'sequencing',
                                                   'issue'  : 'Phred scores across sequences are insufficient quality',
                                                   },
                                                {  'sample' : '4321STDY4321099',
                                                   'qc'     : 'DNA',
                                                   'issue'  : 'DNA concentration 7nM  required >= 10nM',
                                                   },
                                                ]
                                 },
                              {  'sequenced' : mock_sequencing_status[2]['completed']-len(mock_sequencing_status[2]['failed']),
                                 'running'   : 25,
                                 'completed' : 98,
                                 'failed'    : []
                                 },
                              {  'sequenced' : mock_sequencing_status[3]['completed']-len(mock_sequencing_status[3]['failed']),
                                 'running'   : 0,
                                 'completed' : 0,
                                 'failed'    : []
                                 },
                              {  'sequenced' : mock_sequencing_status[4]['completed']-len(mock_sequencing_status[4]['failed']),
                                 'running'   : 105,
                                 'completed' : 179,
                                 'failed'    : [{  'sample' : '4321STDY4321099',
                                                   'qc'     : 'DNA',
                                                   'issue'  : 'DNA concentration 7nM  required >= 10nM',
                                                   },
                                                {  'sample' : '4321STDY4334078',
                                                   'qc'     : 'sequencing',
                                                   'issue'  : 'Phred scores across sequences are insufficient quality',
                                                   },
                                                ]
                                 },
                              {  'sequenced' : mock_sequencing_status[5]['completed']-len(mock_sequencing_status[5]['failed']),
                                 'running'   : 53,
                                 'completed' : 54,
                                 'failed'    : [{  'sample' : '4321STDY4321099',
                                                   'qc'     : 'DNA',
                                                   'issue'  : 'DNA concentration 7nM  required >= 10nM',
                                                   },
                                                {  'sample' : '4321STDY4334078',
                                                   'qc'     : 'sequencing',
                                                   'issue'  : 'Phred scores across sequences are insufficient quality',
                                                   },
                                                {  'sample' : '4321STDY4321099',
                                                   'qc'     : 'DNA',
                                                   'issue'  : 'DNA concentration 7nM  required >= 10nM',
                                                   },
                                                ]
                                 },   
                              ]


class ProtocolError(Exception):
    pass

class Client:
   
   base_url="http://ts24.dev.pam.sanger.ac.uk:5000/"
   
   
   def get_progress(self):
      data = self.make_request('data/juno-progress/', required_keys=['months', 'samples received', 'samples sequenced'])
      return data


   def get_institutions(self):
      data = self.make_request('data/institutions/', required_keys=['institutions'])
      return data['institutions']
   
   
   def get_batches(self):
      data = self.make_request('data/batches/', required_keys=['batches'])
      return data['batches']


   def make_request(self, endpoint, required_keys=[]):
      
      request_url = self.base_url+endpoint
      
      try:
         with urllib.request.urlopen(request_url) as this_response:
            response_as_string = this_response.read().decode('utf-8')
            response_data = json.loads(response_as_string)
            data=response_data.get('data')
            success=response_data.get('success')
            if None == data or None == success:
               error_message = "badly formed JSON response object: missing `data` and/or 'success' keys"
               raise ProtocolError(error_message)
            if not success:
               # expect 'data' to contain an error message of some sort
               error_message = "request to '{}' failed: {}".format(endpoint, data)
               raise ProtocolError(error_message)               
            for required_key in required_keys:
               try:
                  data[required_key]
               except KeyError:
                  error_message = "response data not contain the expected key '{}'".format(required_key)
                  raise ProtocolError(error_message)
            return(data)
         
      except urllib.error.HTTPError:
         # insert any logging/error handling code we want here
         raise
      
      return data
