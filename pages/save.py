import streamlit as st
import json

# Load the JSON as a dictionary
json_dict = json.loads('''{
  "Funding the Balance Sheet": {
    "content": "\n\nThe objective of the treasury is to fund the balance sheet as cheaply as possible taking into account the marginal impact of these actions. The treasury should deploy and invest the deposit liabilities, internal generation and cash flows from maturing assets for optimum return on appropriate maturities either current or forward basis consistent with the bank’s risk policies/appetite. The treasury should also identify and borrow on the best terms from the market to meet the clearing deficits of the bank. The front office of the treasury is responsible for managing investment and market risks in accordance with guidance received from the bank’s ALCO. This is undertaken through the Dealing Room which acts as the bank’s interface to international and domestic financial markets. The mid-office is responsible for onsite risk measurement, monitoring and management reporting, while the back-office is responsible for deal slip verification, generation and dispatch of interbank confirmations, monitoring receipt of confirmations from counterparty banks, effecting/receiving payments, settlement through CCIL or direct through nostro as applicable, monitoring receipt of forex funds in interbank contracts, statutory reports to the RBI, and management of nostro funds to advise latest funds position to the front office.",
    "Subtopics": [
      {
        "content": "\nThe Cash Reserve Ratio (CRR) is a statutory reserve requirement that banks must maintain with the Reserve Bank of India. Banks are required to maintain a certain percentage of their total deposits in the form of cash reserves with the RBI. This is done to ensure that banks have enough liquidity to meet their obligations and to maintain financial stability.",
        "Subtopic": "Cash Reserve Ratio (CRR)"
      },
      {
        "content": "\nLoans and advances, deposits (current and savings accounts and fixed deposits), and other contractual agreements between the bank and its borrowers do not form a part of the treasury portfolio of the bank and should not be included for DTL/NDTL computation. The back office is responsible for ensuring settlement of all deals executed by the front office, and for verifying deal slips, generating and dispatching interbank confirmations, monitoring receipt of confirmations from counterparty banks, effecting/receiving payments, and settlement through CCIL or direct through nostro as applicable.",
        "Subtopic": "Liabilities not to be included for DTL/NDTL computation"
      },
      {
        "content": "\nExempted categories refer to certain types of financial transactions that are exempt from certain regulations or taxes. Examples of exempted categories include certain types of foreign exchange derivatives, such as currency and interest rate swaps, and cross currency hedge products. These products provide clients with the desired interest savings, but also come with inherent risks that must be managed.",
        "Subtopic": "Exempted Categories"
      },
      {
        "content": "\nDemand liabilities refer to the short-term liabilities of a bank, such as call/notice/term money, certificate of deposits, and Tier II bonds. These liabilities are typically used to fund the balance sheet of the bank as cheaply as possible.",
        "Subtopic": "Demand Liabilities"
      },
      {
        "content": "\nTime liabilities are borrowings from the money (or debt) market that are managed by the front office of a treasury. Examples of time liabilities include call/notice money borrowings, term money borrowings, certificate of deposit issues, inter-bank participation certificates, and reverse repos/CBLO-backed borrowing through CCIL. The front office is responsible for managing investment and market risks in accordance with guidance received from the bank’s ALCO, and for entering into transactions on the basis of current market price. The mid-office is responsible for onsite risk measurement, monitoring and management reporting, while the back-office is responsible for deal slip verification, generation and dispatch of interbank confirmations, monitoring receipt of confirmations from counterparty banks, and effecting/receiving payments.",
        "Subtopic": "Time Liabilities"
      },
      {
        "content": "\nOther Demand and Time Liabilities are not mentioned in the context information, however, the back office functions include deal slip verification, generation and dispatch of interbank confirmations, monitoring receipt of confirmations from counterparty banks, monitoring receipt of confirmations of forward contracts, effecting/receiving payments, settlement through CCIL or direct through nostro as applicable, monitoring receipt of forex funds in interbank contracts, and statutory reports to the RBI.",
        "Subtopic": "Other Demand and Time Liabilities"
      },
      {
        "content": "\nThe banking system's treasury assets include G-Secs (T-bills, Central and State Government Securities), Commercial Paper, Certificates of Deposit, SLR Bonds, Non-SLR Bonds, Pass Through Certificates, Equity Shares, REPO, Bills rediscounted, CBLO lendings, Call Lendings, Asset-backed Securities (PTCs) or Collateralized Debt Obligations (CDO), Private Placements, Floating Rate Bonds, Tax-free Bonds, Preference Shares, Listed/Unlisted Equity, Mutual Funds, and Investment in Subsidiaries/Joint Ventures. These assets are managed by the Front Office, which is responsible for liquidity position, fund flows, and maintenance of reserve requirement/s. Risk managers should be posted in treasury to evaluate scenarios, review line/limit excess, review transactions to ensure compliance with regulations, and monitor risk factors such as credit risk, liquidity risk, interest rate risk, and operational risk. The Mid-Office is responsible for onsite risk measurement, monitoring, and management reporting, while the Back-Office is responsible for deal slip verification, generation and dispatch of interbank confirmations, monitoring receipt of confirmations from counterparty banks, effecting/receiving payments, settlement through CCIL or direct through nostro as applicable, monitoring receipt of forex funds in interbank contracts, statutory reports to the RBI, and management of nostro funds.",
        "Subtopic": "Assets with the Banking System"
      },
      {
        "content": "\nBanks in India are able to raise foreign currency funds either through direct commercial borrowing or through use of export credit agency schemes. Customers are also able to reduce the interest costs through embedded options or arrear swaps.",
        "Subtopic": "Borrowings from abroad by banks in India"
      },
      {
        "content": "\nThe context does not mention any information about arrangements with correspondent banks for remittance facilities.",
        "Subtopic": "Arrangements with Correspondent Banks for Remittance Facilities"
      },
      {
        "content": "\nThe cost of CRR maintenance is the cost associated with maintaining the statutory reserve requirement (CRR) set by the Reserve Bank of India. Banks are required to maintain a certain percentage of their deposits as CRR with the RBI. Banks are required to pay interest on the CRR maintained with the RBI, which is determined by the RBI from time to time.",
        "Subtopic": "Cost of CRR Maintenance"
      },
      {
        "content": "\nPenalties for CRR Shortfall are imposed by the Reserve Bank of India (RBI) on banks that fail to maintain the required level of Cash Reserve Ratio (CRR). Banks are required to pay a penalty of 0.5% of the shortfall amount for every week or part of a week that the shortfall persists.",
        "Subtopic": "Penalties for CRR Shortfall"
      }
    ]
  },
  "Clearing Corporation of India Limited (CCIL)": {
    "content": "\n\nCCIL is mentioned in the context information as a platform for Repos/CBLO-backed lending and borrowing. Repos/CBLO-backed lending and borrowing is a type of treasury activity that is facilitated by CCIL. The back office of a treasury is responsible for deal slip verification, generation and dispatch of interbank confirmations, monitoring receipt of confirmations from counterparty banks, effecting/receiving payments, and settlement through CCIL or direct through nostro as applicable.",
    "Subtopics": [
      {
        "content": "\nNetting/Elimination of Exposures is a risk management technique used by treasuries to reduce the risk associated with financial transactions. It involves offsetting the exposures of two counterparties in a transaction, thus reducing the overall risk. This technique is used to reduce the counterparty risk and issuer risk. It is also used to reduce the liquidity risk and price risk.",
        "Subtopic": "Netting/Elimination of Exposures"
      },
      {
        "content": "\nThe organizational structure of a commercial bank treasury should facilitate the handling of all market operations, from dealing to settlement, custody and accounting, in both the domestic and foreign exchange markets. The treasury should be headed by an appropriate senior executive who directs, controls and co-ordinates the activities of the treasury. The Front Office reports to him and is fully responsible for the management of funds, investments and forex activity. The Front Office looks into the liquidity position, fund flows, and maintenance of reserve requirement/s. Risk managers should be posted in treasury for facilitating the evaluation of scenarios, independent review of line/limit excess, reviews of transactions to ensure compliance with regulations, monitor risk factors – credit risk, liquidity risk, interest rate risk, operational risk - in the transactions and give guidance to the front line, viz., dealers to remain in touch with product and market developments. The Head of Back Office will not report to Head of Treasury, but instead to a different vertical Head, like Head of Operations. This ensures that there is independence of reporting of all three verticals right up to apex level. The key functions of the Back Office include deal slip verification, generation and dispatch of interbank confirmations, monitoring receipt of confirmations from counterparty banks, monitoring receipt of confirmations of forward contracts, effecting/receiving payments, settlement through CCIL or direct through nostro as applicable, monitoring receipt of forex funds in interbank contracts, statutory reports to the RBI, and management of nostro funds to advise latest funds position to.",
        "Subtopic": "Network"
      },
      {
        "content": "\nDelivery Versus Payment III (DVP III) Settlement for Securities is not mentioned in the context information provided.",
        "Subtopic": "Delivery Versus Payment III (DVP III) Settlement for Securities"
      },
      {
        "content": "\nReal Time Gross Settlement (RTGS) is not mentioned in the context information.",
        "Subtopic": "Real Time Gross Settlement (RTGS)"
      },
      {
        "content": "\n\nThe Indian financial network is regulated by the Reserve Bank of India (RBI). Banks are required to maintain a stipulated Cash Reserve Ratio (CRR) and Statutory Liquidity Ratio (SLR). Banks are also free to price most of their assets and liabilities by themselves, with the exception of pricing of loans under Differential Interest Rate scheme. The treasury operations also include providing of cover to the customers of the bank in respect of their foreign exchange exposure for their trade transactions like exports, imports, remittances, etc., and extending products and services to its customers for hedging the interest rate risks. The treasury also has the responsibility for setting targets for balance sheet size and key ratios, in consultation with all business groups. Funds management by the treasury involves providing a balanced and well diversified liability base to fund the various assets in the balance sheet of the bank. In terms of its price sensitivity to interest rate changes, needs to be quantified and periodically monitored by means of analytical tools such as duration analysis. This will give a measure of the precise risk profile of the security holdings, and enable the portfolio manager to initiate suitable corrective action in line with the treasury’s overall investment strategy and risk return parameters. As part of the Advanced Approach/Internal Models Approach to Market Risk management under the BIS standards, the Treasury needs to graduate to more sophisticated tools than Duration like Value at Risk (VaR) and ensure their robustness. Along with investment for statutory reserves, the treasury also makes investments in various other kinds of instruments such as Certificate of Deposits, Commercial Papers, Public Sector Bonds, Units of mutual funds, Corporate Debts, equity shares etc. These investment decisions depend on factors such as bank’s liquidity position, money market condition, tenor of funding available, market liquidity in various instruments, yield and tax planning requirements. Treasury may hold investment in these instruments till their maturity, or it can trade in them to take advantage of market opportunities. Trading and Distribution skills are keys to the success of any treasury. Tradability provides liquidity in various instruments and generates non-interest income. With increasing competition among banks, spreads in traditional banking products are shrinking. On the other hand, cost of various liabilities is rising. As a consequence, traditional fund-based income of banks is gradually being eroded. With the onset of reforms, it is also seen that there is an increasing trend towards disintermediation in the financial markets. Borrowers are directly accessing market through the medium of debt instruments like CPs, debentures, etc., or through forex/external borrowings. Moreover, fund-based exposures require balance sheet growth, and that in turn entails higher capital adequacy requirements. In such a situation, non-fund based revenue gains greater importance. It is here that the strength of the treasury lies. It can help to transform a borrower of funds into an issuer of debt. It can then distribute these debt instruments to investors who were till now only depositors. This will enable the bank to earn a fee income without any balance sheet growth and without locking up funds of its own. Trading in instruments creates more liquidity and increases investor appetite. This has been the trend in financial markets the world over. Securitisation of debt is likely to be an important growth area in the Indian market too in the near future. In the present day competitive environment, treasury cannot afford to lose its customer focus. In addition to trading avenues, which are essentially volatile in nature, treasury now requires non-volatile sources of revenue which are reflected in the diversified customer base of the bank. With the growing liberalization and the opening up of the economy to international financial markets and investors, the treasury departments of various banks now function in a multi-product, multi-currency environment and cater to the multiple needs of its customers. There is bound to be a pressure on the treasury to offer various rupee-based and cross currency hedge products to their clients who have foreign currency exposures on their balance sheets. In fact, the recent changes in the regulations would, over a period of time, ensure the convergence of local currency and foreign currency yield curves and enable the clients to manage their foreign currency assets and liabilities in a more profitable manner through the use of foreign exchange derivatives both in the area of currency and interest rates. Customers today, with the help of the Foreign Exchange Unit of the Treasury, are able to raise foreign currency funds either through direct commercial borrowing or through use of export credit agency schemes and are also able to reduce the interest costs through embedded options or arrear swaps. While these products provide the client with the much desired interest saving, these are not without inherent risks. It is imperative for the Indian financial network to ensure that these risks are managed effectively.",
        "Subtopic": "Indian Financial Network"
      },
      {
        "content": "\nThe Structured Financial Messaging System (SFMS) is a system used for the settlement of all deals executed by Front Office. It is used to facilitate the evaluation of scenarios, independent review of line/limit excess, reviews of transactions to ensure compliance with regulations, monitor risk factors – credit risk, liquidity risk, interest rate risk, operational risk - in the transactions and give guidance to the front line, viz., dealers to remain in touch with product and market developments. It is also used for deal slip verification, generation and dispatch of interbank confirmations, monitoring receipt of confirmations from counterparty banks, monitoring receipt of confirmations of forward contracts, effecting/receiving payments, settlement through CCIL or direct through nostro as applicable, monitoring receipt of forex funds in interbank contracts, statutory reports to the RBI, and management of nostro funds to advise latest funds position.",
        "Subtopic": "Structured Financial Messaging System (SFMS)"
      },
      {
        "content": "\nPublic Key Infrastructure (PKI) is not mentioned in the context information.",
        "Subtopic": "Public Key Infrastructure (PKI)"
      }
    ]
  },
  "Statutory Liquidity Ratio (SLR)": {
    "content": "\nThe domestic treasury assets comprise G-secs, CPs, CODs, SLR bonds, non-SLR bonds, PTCs, equity shares, Reverse Repo, Bills discounted. Treasury liabilities are Call/Notice/Term money, certificate of deposits, Tier II bonds and Repo. The main objectives of the treasury are to take advantage of attractive trading and arbitrage opportunities in the bond and forex markets, to fund the balance sheet as cheaply as possible, and to assess and advise and manage the financial risks associated with the non-treasury assets and liabilities of the bank and to maintain statutory reserves like CRR and SLR.\n\nStatutory Liquidity Ratio (SLR) is a requirement that banks maintain a certain proportion of their deposits in the form of liquid assets such as cash, gold, and approved securities. SLR bonds are part of the domestic treasury assets and are used to maintain statutory reserves like CRR and SLR.",
    "Subtopics": [
      {
        "content": "\nTreasury assets comprise G-secs, CPs, CODs, SLR bonds, non-SLR bonds, PTCs, equity shares, Reverse Repo, and Bills discounted. Treasury liabilities are Call/Notice/Term money, certificate of deposits, Tier II bonds and Repo. The main objectives of the treasury are to take advantage of attractive trading and arbitrage opportunities in the bond and forex markets, to fund the balance sheet as cheaply as possible, and to assess and advise and manage the financial risks associated with the non-treasury assets and liabilities of the bank and to maintain statutory reserves like CRR and SLR. \n\nThe treasury is responsible for maintaining SLR, which stands for Statutory Liquidity Ratio. This is a requirement set by the Reserve Bank of India that banks must maintain a certain percentage of their deposits in the form of liquid assets, such as government securities, cash, and gold.",
        "Subtopic": "Maintenance of SLR"
      },
      {
        "content": "\nPenalties for SLR shortfall are imposed by the Reserve Bank of India (RBI) on banks that fail to maintain the Statutory Liquidity Ratio (SLR). Banks are required to maintain a certain percentage of their total deposits in the form of liquid assets such as gold, government securities, and other approved securities. If a bank fails to maintain the SLR, it is subject to a penalty of 0.1% of the shortfall amount.",
        "Subtopic": "Penalties for SLR Shortfall"
      }
    ]
  }
}''')

# Loop through each topic in the JSON dictionary
for topic, subtopics_dict in json_dict.items():
    # Get the content for the topic
    content = subtopics_dict['content']
    # Create a text input field for the content and store the updated content in the dictionary
    subtopics_dict['content'] = st.text_input(f"Edit content for {topic}:", value=content)
    # Loop through each subtopic for the topic
    for subtopic_dict in subtopics_dict['Subtopics']:
        subtopic_name = subtopic_dict['Subtopic']
        # Get the content for the subtopic
        content = subtopic_dict['content']
        # Create a text input field for the content and store the updated content in the dictionary
        subtopic_dict['content'] = st.text_input(f"Edit content for subtopic {subtopic_name} under topic {topic} :", value=content)

# Create a "Save" button
if st.button("Save"):
    # Convert the updated dictionary to JSON
    updated_json = json.dumps(json_dict, indent=2)
    # Write the updated JSON to a file or database, or print it to the console
    st.write(json_dict)
