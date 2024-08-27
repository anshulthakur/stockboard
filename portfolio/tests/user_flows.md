* User visit site: is presented with a login screen if not logged in.
Test Cases: 
- Not logged in user always redirects to login page
- Logout takes to login page, which always has the overview page as next page if not requested explicitly

* User logs in and sees the overview page
Test Cases:
- Global portfolio summary must be visible. If nothing is added, this shows 0. Else, correct
  summary must be displayed.
- Summary includes: 
    * Net worth
    * Number of accounts with a call-to-action to detail page
    * Monthly plot of networth
    * Alerts

* User goes to Accounts page from Menu and finds no accounts. Clicks on a button to add new account, and sees a form. Fills the form and an account is created. The page now shows the account summary card and the add account option.
* The user adds other accounts, such as broker, demat, crypto etc.
  - Test that the user cannot add money to demat
  - Test that demat account cannot be created directly. It is always created with a broker's account
  - Test that the user cannot add cash balance (it is a read-only field)

* In each account, the user sees the transactions tab. Can visit the transactions tab to see a short pass-book (initially empty). Plus, a button to add new transaction is available. The user clicks on it and a menu pops up with fields rendered according to the account type. An option to upload bulk transactions for the account is also available. 
  - The user creates a series of transactions
  - The user uploads a transaction file and the account details are updated.

  - Test that there is never a negative balance in the account whether the transactions are added manually or via a bulk file.

Since the transactions may be loaded from external sources, the transaction IDs may be different for each. There should be no duplication of transactions based on transaction IDs. However, the transaction IDs are optional.

* The overview page starts showing summary information.