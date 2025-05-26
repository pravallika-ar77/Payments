import configparser

config = configparser.RawConfigParser()

config.read('msg.properties')

#print(config.sections())
print(config.get('Transaction_Pacs4','tx_pacs4_Amount'))

