@app.route('/api/search', methods=['GET'])
def search():
term = request.args.get('term','').lower()
kategori = request.args.get('kategori','')
which = request.args.get('which','masuk') # masuk | keluar
sheet = 'surat_masuk' if which=='masuk' else 'surat_keluar'
df = sheet_to_df(sheet)
if df.empty:
return jsonify([])
# naive filter: search in no_surat, pengirim/tujuan, keterangan
mask = df.astype(str).apply(lambda row: row.str.contains(term, case=False, na=False)).any(axis=1)
if kategori:
mask = mask & (df['kategori'].astype(str) == kategori)
res = df[mask]
return jsonify(res.fillna('').to_dict(orient='records'))


# --- Laporan: export Excel ---
@app.route('/api/laporan/excel', methods=['GET'])
def laporan_excel():
df_masuk = sheet_to_df('surat_masuk')
df_keluar = sheet_to_df('surat_keluar')
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
if not df_masuk.empty:
df_masuk.to_excel(writer, sheet_name='masuk', index=False)
else:
pd.DataFrame().to_excel(writer, sheet_name='masuk', index=False)
if not df_keluar.empty:
df_keluar.to_excel(writer, sheet_name='keluar', index=False)
else:
pd.DataFrame().to_excel(writer, sheet_name='keluar', index=False)
buffer.seek(0)
return send_file(buffer, download_name='laporan_sidakep.xlsx', as_attachment=True)


# --- Users management (basic) ---
@app.route('/api/users', methods=['GET'])
def list_users():
df = sheet_to_df('users')
if df.empty:
return jsonify([])
return jsonify(df.fillna('').to_dict(orient='records'))


@app.route('/api/users', methods=['POST'])
def create_user():
# expects json: username, password (plain for demo), role
j = request.json
username = j.get('username')
password = j.get('password')
role = j.get('role')
append_row('users', [username, password, role])
return jsonify({'ok':True})


if __name__ == '__main__':
app.run(host='0.0.0.0', port=5000, debug=True)