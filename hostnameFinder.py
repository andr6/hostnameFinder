__author__ = 'ned@shadowserver.org'

import csv
import argparse
import dns.resolver
import multiprocessing

def parse_hostnames():
  '''
  :param none
  :return list of hostnames parsed from static wordlist
  '''
  hostnames = []
  with open('hostname.lst') as hosts:
    for host in hosts.readlines():
      if host.strip() not in hostnames:
        hostnames.append(host.strip())
  return hostnames

def build_fqdns(hostnames, domain):
  '''
  :param list of hostnames parsed from static wordlist:
  :param user supplied domain:
  :return list of fqdns derived from hostname list and user supplied domain
  '''
  fqdnList = []
  for host in hostnames:
    fqdn = '%s.%s' %(host,domain)
    if fqdn not in fqdnList:
      fqdnList.append(fqdn)
  return fqdnList

def enumnerate_fqdns(fqdn):
  resolution = {}
  '''
  :param list of fqdns fed via Pool:
  :return A record
  '''
  try:
    resolver = dns.resolver.Resolver()
    resolver.nameserver = '8.8.8.8'
    answer = resolver.query(fqdn,'A')
    for data in answer:
      resolution[fqdn] = data.address
    return resolution
  except Exception, e:
    pass

def main():
  parser = argparse.ArgumentParser(description='Brute force lookup for unknown hosts at known domain')
  parser.add_argument('domain',help='domain to resolve')
  args = parser.parse_args()
  if args.domain:
    fqdnList = build_fqdns(parse_hostnames(),args.domain)

  filename = '%s_resolutions.csv'  %args.domain
  resolutions = open(filename,'w+')
  writer = csv.writer(resolutions)
  pool = multiprocessing.Pool(100)
  for fqdn in pool.map(enumnerate_fqdns,fqdnList):
    if fqdn != None:
      for k, v in fqdn.iteritems():
        print '%s %-20s : %s' %('[+]', k, v)
        result = (k, v)
        writer.writerow(result)
  resolutions.close()

if __name__ == '__main__':
  main()