import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("Key.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()


if "login" not in st.session_state:
    st.session_state["login"] = False

if st.session_state["login"]:
    st.title("태신의 이것저것")

else:
    tab1, tab2 = st.tabs(["로그인","회원가입"])
    with tab1:
        st.header("로그인")
        login_id=st.text_input("ID", key = "login_id")
        login_pw=st.text_input("PW", type = "password", key = "login_pw")

        if st.button("로그인"):
            if not login_id or not login_pw:
                st.warning("아이디 또는 비밀번호를 입력해주세요.")
        
            else:
                user_doc = db.collection("users").document(login_id).get()
                if user_doc.exists and user_doc.to_dict()["password"] == login_pw:
                    st.session_state["login"] = True
                    st.session_state["user_id"] = login_id
                    st.rerun()
                else:
                    st.error("아이디 또는 비밀번호가 일치하지 않습니다.")

    with tab2:
        st.header("회원가입")
        username = st.text_input("이름", key="username")
        new_id = st.text_input("사용할 아이디", key="new_id")
        new_pw = st.text_input("사용할 비밀번호", type="password", key="new_pw")
        confirm_pw = st.text_input("비밀번호 확인", type="password", key="confirm_pw")

        if st.button("회원가입"):
            if new_pw != confirm_pw:
                st.error("비밀번호가 일치하지 않습니다.")

            elif not username:
                st.error("성함을 입력해주세요.")
            
            elif not new_id or not new_pw:
                st.error("아이디 또는 비밀번호를 입력해주세요.")

            else:
                db.collection("users").document(new_id).set({"username": username, "password": new_pw})
                st.success("회원가입 완료! 로그인 탭에서 접속하세요.")

if st.session_state["login"]:
    if st.button("응원받기"):
            st.balloons()

    with st.sidebar:
        st.header("설정메뉴")

        if st.button("로그아웃"):
            st.session_state["login"] = False
            st.rerun()

        if st.button("회원탈퇴",key="delete"):
            db.collection("users").document(st.session_state["user_id"]).delete()
            st.session_state["login"] = False
            st.rerun()

    intab1, intab2 = st.tabs(["메모장","계산기"])
    with intab1:
        st.title("태신의 메모장")

        selected_date = st.date_input("목표를 행할 날짜를 선택하세요", key="calender_date")
        date_str = selected_date.strftime("%Y-%m-%d")                                           #날짜를 문자열로 변환

        with st.form("todos"):
            selbox = st.selectbox("카테고리",["업무","개인"])
            task = st.text_input("할 일을 적으세요.")
            sub = st.form_submit_button("추가")

        if sub:
            st.write("정상적으로 추가되었습니다")

        if sub and task:
            db.collection("todos").add({
                "date" : date_str,
                "style" : selbox,
                "content" : task,
                "at": firestore.SERVER_TIMESTAMP
            })
            st.rerun()

        docs = db.collection("todos").stream()
        for doc in docs:
            todo = doc.to_dict()

            col1, col2, col3 = st.columns([2,5,1])

            with col1:
                st.info(todo["date"])

            with col2:
                st.info(f"[{todo["style"]}] {todo["content"]}")

            with col3:
                if st.button("삭제",key=doc.id):
                    db.collection("todos").document(doc.id).delete()
                    st.success("정상적으로 삭제되었습니다.")
                    st.rerun()

    with intab2:
        if st.button("회원탈퇴",key="del"):
            db.collection("users").document(st.session_state["user_id"]).delete()
            st.session_state["login"] = False
            st.rerun()

        with st.form("numbers"):
            c_num, c_sel, c_num1 = st.columns([2,1,2])

            with c_num:
                num = st.number_input("숫자1",value = 0)
            with c_sel:
                sel = st.selectbox("연산",["+","-","*","/"]) 
            with c_num1:
                num1 = st.number_input("숫자2",value = 0)
            submit = st.form_submit_button("계산")

        
        if submit:
            num_error = False
            result = 0

            if sel == "+":
                result = num + num1
            elif sel == "-":
                result = num - num1
            elif sel == "*":
                result = num * num1
            elif sel == "/":
                if num1 != 0:
                    result = num / num1
                else:
                    st.warning("0으로 나눌 수 없습니다.")
                    num_error = True
            
            if submit and not num_error:
                db.collection("numbers").add({
                "num":num,
                "num1":num1,
                "sel":sel,
                "result":result
                })
                st.success(f"결과: {num}{sel}{num1} = {result}")
                st.rerun()

        nums = db.collection("numbers").stream()
        for a in nums:
            main = a.to_dict()
            cel1, cel2 = st.columns([6,2])

            with cel1:
                st.info(f"{main['num']} {main['sel']} {main['num1']} = {main['result']}")

            with cel2:
                if st.button("제거", key=a.id):
                    db.collection("numbers").document(a.id).delete()
                    st.success("정상적으로 삭제되었습니다.")
                    st.rerun()
