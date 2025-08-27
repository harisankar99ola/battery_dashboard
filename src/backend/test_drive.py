from drive_handler import GoogleDriveHandler

handler = GoogleDriveHandler()
print('Testing basic folder listing...')
items = handler.list_folder_contents('1Ixvo_rJZ_9jni3R6HdAJnL_gvEF4tI5l')
print(f'Found {len(items)} items:')

for item in items[:10]:
    print(f'- {item["name"]} ({item["mimeType"]})')

print('\nTesting battery test folders...')
folders = handler.get_battery_test_folders('1Ixvo_rJZ_9jni3R6HdAJnL_gvEF4tI5l')
print(f'Found {len(folders)} battery test folders:')
for folder in folders[:5]:
    print(f'- {folder["name"]} ({folder["file_count"]} files)')

# Check what's in the first folder
print('\nChecking contents of first folder...')
first_folder = [item for item in items if item['mimeType'] == 'application/vnd.google-apps.folder'][0]
print(f'Checking folder: {first_folder["name"]}')
sub_items = handler.list_folder_contents(first_folder['id'])
print(f'Found {len(sub_items)} items in folder:')
for item in sub_items[:10]:
    print(f'- {item["name"]} ({item["mimeType"]})')

# Check CSV files specifically
csv_files = [item for item in sub_items if item['name'].lower().endswith('.csv')]
print(f'\nCSV files in folder: {len(csv_files)}')
for csv_file in csv_files[:5]:
    print(f'- {csv_file["name"]}')
