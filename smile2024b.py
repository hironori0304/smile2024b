import streamlit as st
import pandas as pd

# 初期化
if 'food_data' not in st.session_state:
    st.session_state.food_data = pd.DataFrame(columns=['食品名', 'エネルギー（kcal）', 'たんぱく質（g）', '脂質（g）', '炭水化物（g）', '食塩相当量（g）'])
if 'selected_foods' not in st.session_state:
    st.session_state.selected_foods = pd.DataFrame(columns=['食品名', '重量（g）', 'エネルギー（kcal）', 'たんぱく質（g）', '脂質（g）', '炭水化物（g）', '食塩相当量（g）'])

st.title("栄養価計算アプリSmile")

# サイドバーのページ選択
page = st.sidebar.selectbox("ページを選択", ["食品データベース登録", "栄養価計算"])

# 食品データベースのアップロード機能
uploaded_file = st.sidebar.file_uploader("食品データベースをアップロード", type=['csv'])
if uploaded_file is not None:
    uploaded_data = pd.read_csv(uploaded_file)
    # アップロードされたデータとセッションのデータをマージ（重複を削除）
    st.session_state.food_data = pd.concat([st.session_state.food_data, uploaded_data]).drop_duplicates().reset_index(drop=True)

if page == "食品データベース登録":
    # データベース登録用のフォームをサイドバーに表示
    st.sidebar.subheader("新規食品の登録")
    with st.sidebar.form("food_form"):
        food_name = st.text_input("食品名")
        energy = st.number_input("エネルギー（kcal）", min_value=0.0)
        protein = st.number_input("たんぱく質（g）", min_value=0.0)
        fat = st.number_input("脂質（g）", min_value=0.0)
        carbs = st.number_input("炭水化物（g）", min_value=0.0)
        salt = st.number_input("食塩相当量（g）", min_value=0.0)
        submitted = st.form_submit_button("登録")

    # 入力された食品情報を追加
    if submitted and food_name:
        new_food = pd.DataFrame({
            '食品名': [food_name],
            'エネルギー（kcal）': [energy],
            'たんぱく質（g）': [protein],
            '脂質（g）': [fat],
            '炭水化物（g）': [carbs],
            '食塩相当量（g）': [salt]
        })
        # 重複チェックをして新しいデータを追加
        if not st.session_state.food_data['食品名'].isin([food_name]).any():
            st.session_state.food_data = pd.concat([st.session_state.food_data, new_food], ignore_index=True)

        else:
            st.warning(f"{food_name} はすでに登録されています！")

    # メイン画面に食品データを表示
    st.subheader("食品データベース")
    if not st.session_state.food_data.empty:
        st.dataframe(st.session_state.food_data)

        # CSVダウンロード機能の追加
        @st.cache_data
        def convert_df(df):
            return df.to_csv(index=False).encode('utf-8-sig')

        csv = convert_df(st.session_state.food_data)

        st.download_button(
            label="CSVファイルとしてダウンロード",
            data=csv,
            file_name='food_database.csv',
            mime='text/csv'
        )
    else:
        st.write("現在、食品データベースにはデータがありません。")

elif page == "栄養価計算":
    # 栄養価計算のフォームをサイドバーに表示
    st.sidebar.subheader("栄養価計算")
    uploaded_results = st.sidebar.file_uploader("既存データをアップロード", type=['csv'])

    if uploaded_results is not None:
        # アップロードされたデータを読み込む
        uploaded_data = pd.read_csv(uploaded_results)
        # 合計行を削除（「合計」として識別する）
        uploaded_data = uploaded_data[uploaded_data['食品名'] != '合計']
        # アップロードしたデータをセッションステートに格納
        st.session_state.selected_foods = pd.concat([st.session_state.selected_foods, uploaded_data]).drop_duplicates().reset_index(drop=True)

    # 食品データベースが空でない場合
    if not st.session_state.food_data.empty:
        # 食品の選択
        food_options = st.session_state.food_data['食品名'].tolist()
        selected_food = st.sidebar.selectbox("食品を選択", food_options)
        # 重量の入力
        weight = st.sidebar.number_input("重量（g）", min_value=0.0)
        # 材料の説明を入力するためのテキストボックス
        material_description = st.sidebar.text_input("材料の説明", "")

        if st.sidebar.button("追加"):
            if selected_food and weight > 0:
                food_info = st.session_state.food_data[st.session_state.food_data['食品名'] == selected_food].iloc[0]
                # 栄養価計算（重量に基づいて計算）
                calculated_food = pd.DataFrame({
                    '食品名': [selected_food],
                    '重量（g）': [weight],
                    'エネルギー（kcal）': [food_info['エネルギー（kcal）'] * (weight / 100)],
                    'たんぱく質（g）': [food_info['たんぱく質（g）'] * (weight / 100)],
                    '脂質（g）': [food_info['脂質（g）'] * (weight / 100)],
                    '炭水化物（g）': [food_info['炭水化物（g）'] * (weight / 100)],
                    '食塩相当量（g）': [food_info['食塩相当量（g）'] * (weight / 100)],
                    '材料の説明': [material_description]  # 材料の説明を追加
                })

                # selected_foods に新しい食品を追加（リセットせずに追加する）
                st.session_state.selected_foods = pd.concat([st.session_state.selected_foods, calculated_food], ignore_index=True)

    # リセットボタン
    if st.button("リセット"):
        st.session_state.selected_foods = pd.DataFrame(columns=['食品名', '重量（g）', 'エネルギー（kcal）', 'たんぱく質（g）', '脂質（g）', '炭水化物（g）', '食塩相当量（g）', '材料の説明'])
        st.success("リセットされました。")

    # 選択された食品リストを表示
    if not st.session_state.selected_foods.empty:
        st.subheader("選択された食品リスト")

        # 食品の削除、上移動、下移動機能
        selected_index = st.selectbox("移動または削除する食品を選択", range(len(st.session_state.selected_foods)), format_func=lambda x: st.session_state.selected_foods['食品名'].iloc[x])
        
        if st.button("削除"):
            st.session_state.selected_foods = st.session_state.selected_foods.drop(selected_index).reset_index(drop=True)
            st.success("食品が削除されました。")

        if st.button("上に移動"):
            if selected_index > 0:
                # 上に移動
                st.session_state.selected_foods.iloc[[selected_index, selected_index - 1]] = st.session_state.selected_foods.iloc[[selected_index - 1, selected_index]].values
                st.success("食品が上に移動しました。")
            else:
                st.warning("最上部の食品は移動できません。")

        if st.button("下に移動"):
            if selected_index < len(st.session_state.selected_foods) - 1:
                # 下に移動
                st.session_state.selected_foods.iloc[[selected_index, selected_index + 1]] = st.session_state.selected_foods.iloc[[selected_index + 1, selected_index]].values
                st.success("食品が下に移動しました。")
            else:
                st.warning("最下部の食品は移動できません。")

        # 合計行を計算
        total_selected = st.session_state.selected_foods[['重量（g）', 'エネルギー（kcal）', 'たんぱく質（g）', '脂質（g）', '炭水化物（g）', '食塩相当量（g）']].sum()
        total_row = pd.DataFrame({
            '食品名': ['合計'],
            '重量（g）': [total_selected['重量（g）']],
            'エネルギー（kcal）': [total_selected['エネルギー（kcal）']],
            'たんぱく質（g）': [total_selected['たんぱく質（g）']],
            '脂質（g）': [total_selected['脂質（g）']],
            '炭水化物（g）': [total_selected['炭水化物（g）']],
            '食塩相当量（g）': [total_selected['食塩相当量（g）']],
            '材料の説明': ['']  # 合計行には材料の説明は不要
        })

        # 表示
        result_table = pd.concat([st.session_state.selected_foods, total_row], ignore_index=True)
        st.dataframe(result_table)

        # CSVダウンロード機能の追加（合計を含む）
        @st.cache_data
        def convert_selected_df(df):
            # 合計行を含めてCSVに変換
            total_selected = df[['重量（g）', 'エネルギー（kcal）', 'たんぱく質（g）', '脂質（g）', '炭水化物（g）', '食塩相当量（g）']].sum()
            total_row = pd.DataFrame({
                '食品名': ['合計'],
                '重量（g）': [total_selected['重量（g）']],
                'エネルギー（kcal）': [total_selected['エネルギー（kcal）']],
                'たんぱく質（g）': [total_selected['たんぱく質（g）']],
                '脂質（g）': [total_selected['脂質（g）']],
                '炭水化物（g）': [total_selected['炭水化物（g）']],
                '食塩相当量（g）': [total_selected['食塩相当量（g）']],
                '材料の説明': ['']  # 合計行には材料の説明は不要
            })
            return pd.concat([df, total_row], ignore_index=True).to_csv(index=False).encode('utf-8-sig')

        # ダウンロードボタン
        csv = convert_selected_df(st.session_state.selected_foods)
        st.download_button("結果をダウンロード", csv, "nutrition_calculation_results.csv", "text/csv")
