import json
import urllib.parse
import urllib.request

class ProtocolError(Exception):
    pass


class Mock:

   def get_progress(self):
      return   {  'months'             : [1,2,3,4,5,6,7,8,9],
                  'samples received'   : [158,225,367,420,580,690,750,835,954],
                  'samples sequenced'  : [95,185,294,399,503,640,730,804,895],
                  }

   def get_institutions(self):
      return   {  'Sydney':     'University of Sydney',
                  'Keio':       'Keio University School of Medicine',
                  'HK':         'Chinese University of Hong Kong',
                  'CHRF':       'Child Health Research Foundation',
                  'Peradeniya': 'University of Peradeniya',
                  'Gondar':     'University of Gondar',
                  }
   
   def get_batches(self):
      return   {  'Sydney'      : { 'expected'  : 800,
                                    'received'  : 188,
                                    'deliveries': [{'name': 'batch 1', 'date': '3 Dec 2020',  'number': 95  },
                                                   {'name': 'batch 2', 'date': '11 Jan 2021', 'number': 93  },
                                                   ]
                                    },
                  'CHRF'        : { 'expected'  : 1200,
                                    'received'  : 668,
                                    'deliveries': [{'name': 'batch 1', 'date': '24 Nov 2020', 'number': 237 },
                                                   {'name': 'batch 2', 'date': '16 Dec 2020', 'number': 175 },
                                                   {'name': 'batch 3', 'date': '3 Jan 2021',  'number': 194 },
                                                   ]
                                    },
                  'HK'          : { 'expected'  : 900,
                                    'received'  : 232,
                                    'deliveries': [{'name': 'batch 1', 'date': '28 Dec 2020', 'number': 104 },
                                                   {'name': 'batch 2', 'date': '27 Jan 2021', 'number': 128 },
                                                   ]
                                    },
                  'Keio'        : { 'expected'  : 1500,
                                    'received'  : 341,
                                    'deliveries': [{'name': 'batch 1', 'date': '25 Feb 2021', 'number': 341 },
                                                   ]
                                    },
                  'Peradeniya'  : { 'expected'  : 1000,
                                    'received'  : 505,
                                    'deliveries': [{'name': 'batch 1', 'date': '30 Oct 2020', 'number': 76  },
                                                   {'name': 'batch 2', 'date': '24 Nov 2020', 'number': 85  },
                                                   {'name': 'batch 3', 'date': '17 Dec 2020', 'number': 105 },
                                                   {'name': 'batch 4', 'date': '11 Jan 2021', 'number': 128 },
                                                   {'name': 'batch 5', 'date': '3 Feb 2021',  'number': 111 },
                                                   ]
                                    },
                  'Gondar'      : { 'expected'  : 600,
                                    'received'  : 203,
                                    'deliveries': [{'name': 'batch 1', 'date': '17 Jan 2020', 'number': 203 },
                                                   ]
                                    },
                  }
                                    
   def get_sequencing_status(self):
      batches=self.get_batches()
      return   {  'Sydney'      : { 'received'  : batches['Sydney']['received'],
                                    'completed' : 173,
                                    'failed'    : []
                                    },
                  'CHRF'        : { 'received'  : batches['CHRF']['received'],
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
                  'HK'          : { 'received'  : batches['HK']['received'],
                                    'completed' : 198,
                                    'failed'    : []
                                    },
                  'Keio'        : { 'received'  : batches['Keio']['received'],
                                    'completed' : 0,
                                    'failed'    : []
                                    },
                  'Peradeniya'  : { 'received'  : batches['Peradeniya']['received'],
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
                  'Gondar'      : { 'received'  : batches['Gondar']['received'],
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
                  }

   def get_pipeline_status(self):
      status=self.get_sequencing_status()
      return   {  'Sydney'      : { 'sequenced' : status['Sydney']['completed']-len(status['Sydney']['failed']),
                                    'running'   : 30,
                                    'completed' : 63,
                                    'failed'    : []
                                    },
                  'CHRF'        : { 'sequenced' : status['CHRF']['completed']-len(status['CHRF']['failed']),
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
                  'HK'          : { 'sequenced' : status['HK']['completed']-len(status['HK']['failed']),
                                    'running'   : 25,
                                    'completed' : 98,
                                    'failed'    : []
                                    },
                  'Keio'        : { 'sequenced' : status['Keio']['completed']-len(status['Keio']['failed']),
                                    'running'   : 0,
                                    'completed' : 0,
                                    'failed'    : []
                                    },
                  'Peradeniya'  : { 'sequenced' : status['Peradeniya']['completed']-len(status['Peradeniya']['failed']),
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
                  'Gondar'      : { 'sequenced' : status['Gondar']['completed']-len(status['Gondar']['failed']),
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
                  }


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
