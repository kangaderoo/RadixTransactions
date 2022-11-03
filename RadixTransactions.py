from typing import List, Dict, Any
import radixlib as radix
import os

def main() -> None:
	# Defining the network that we will be connecting to.
	network: radix.network.Network = radix.network.MAINNET
	
	# Creating a new wallet object from random on the network defined.
	wallet: radix.Wallet = radix.Wallet(
		provider = radix.Provider(network),
		signer = radix.Signer.new_random()
	)
	
	# Get all transaction to and from the following address.
	myaccount: str = "rdx1qsp000000000000000000000000000000000000000000000000000q9c0gvj" # Radix burn address
	
	# Creating an empty list to store the transactions and begining to query for the transactions
	transactions_list: List[Dict[str, Any]] = []
	cursor: Optional[str] = None

	f = open('RadixTransactions.csv', 'w')
	f.write("Wallet address: {walletaddress}\n".format(walletaddress=myaccount))
	
	while True:
		query_response: Dict[str, Any] = wallet.provider.get_account_transactions(
			account_address = myaccount,
			limit = 1,
			cursor = cursor
		)
		transactions_list: List[Dict[str, Any]] = query_response.get("transactions")
		for transaction in transactions_list:
			transaction_status : Dict[str, Any] = transaction.get("transaction_status")
			confirmed_time: str = transaction_status.get("confirmed_time")
			transaction_identifier : Dict[str, Any] = transaction.get("transaction_identifier")
			hash: str = transaction_identifier.get("hash")
			metadata: Dict[str: Any] = transaction.get("metadata")
			transaction_message: str = metadata.get("message")
			action_list: List[Dict[str, Any]] = transaction.get("actions")
			for data in action_list:
				direction: str = ""
				otheraddress: str = ""
				type: str = data.get("type")
				if type != "TransferTokens":
					break
				mydata = data.get("from_account")
				if mydata != None:
					myaddress = mydata.get("address")
					if myaddress != None:
						if myaccount == myaddress:
							direction = "out"
						else:
							otheraddress = myaddress
				mydata = data.get("to_account")
				if mydata != None:
					myaddress = mydata.get("address")
					if myaddress != None:
						if myaccount == myaddress:
							direction = "in"
						else:
							otheraddress = myaddress
				transamount = data.get("amount")
				if transamount:
					myvalue: float = float(transamount['value']) / 1e18
					myrri: str = transamount['token_identifier']['rri']
					if direction == "out":
						myvalue = myvalue * -1
				
				plain_text: str = ""
				if transaction_message:
					try:
						plain_text_hex = transaction_message[4:]
						plain_text = bytes.fromhex(plain_text_hex)
#						plain_text = bytes_object.decode("utf-8")
					except:
						plain_text = "decode error"
				if (direction != ""):
					try:
						lineout: str = "%s; %s; %s; %s; %s; %s; %s" % (confirmed_time, hash, direction, otheraddress, myvalue, myrri, plain_text)
						f.write(lineout + "\n")
					except:
						plain_text = "another decode error"
						lineout: str = "%s; %s; %s; %s; %s; %s; %s" % (confirmed_time, hash, direction, otheraddress, myvalue, myrri, plain_text)
						f.write(lineout + "\n")
		cursor = query_response.get('next_cursor')
		if cursor is None:
			break
	f.close()


if __name__ == "__main__":
	main()