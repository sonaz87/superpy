Highlighted elements:
1: Advancing time can happen backwards (but not further back than the current date). For this to work without issues, buying and selling products need to happen not only to the current inventory, but all future days inventories too. So the archive inventories were introduced that hold an inventory item for every day that was within the range of usage. Buying will simply add the product to future days. Selling will not only remove one count on future days, but will also check if there are enough products on stock in the future to make the sale on the current day.
For this concept to work I had to make sure every inventory object in the archive inventory is an actual unique object, and not just a reference, hence the new inventory objetcs are created with copy.deepcopy().

2: The archive inventories could not be handled in a csv fashion (at least not without making it very cumbersome to work with) so the objects it stores are serialized with pickle and written to a binary file.

3: I added a hash to the log file which is updated every time any of the files are updated. If any of the files have been tampered with (or corrupted) the application will give a warning and will not start up. If this was a real life application, this could prevent fraud committed with a supermarket inventory. (Although the inventories are themselves stored in a binary file, it would not be impossible to recreate the objects from the binary file and modify their contents.)