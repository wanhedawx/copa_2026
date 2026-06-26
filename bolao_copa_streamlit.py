import streamlit as st
import pandas as pd
import hashlib
import secrets
import html
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import firebase_admin
from firebase_admin import credentials, firestore

# ===================== CONFIG =====================
TZ = ZoneInfo("America/Maceio")
LOCK_HOURS_BEFORE = 1
ADMIN_USER = "ADMIN"
SENHA_PADRAO = "123"

USUARIOS_INICIAIS = [
    "CHEVETTE67",
    "SAPAS",
    "ANAO PIKENO",
    "CHARQUINHO",
    "GAGUINHO",
    "FILHO PREFERIDO",
    "MACACO",
    "REALAL",
]

# ===================== JOGOS =====================
JOGOS = [
    # GRUPO A
    {"id":"A01","data_hora":"2026-06-11 16:00","grupo":"A","mandante":"México","visitante":"África do Sul"},
    {"id":"A02","data_hora":"2026-06-11 23:00","grupo":"A","mandante":"Coreia do Sul","visitante":"República Tcheca"},
    {"id":"A03","data_hora":"2026-06-18 13:00","grupo":"A","mandante":"República Tcheca","visitante":"África do Sul"},
    {"id":"A04","data_hora":"2026-06-18 22:00","grupo":"A","mandante":"México","visitante":"Coreia do Sul"},
    {"id":"A05","data_hora":"2026-06-24 22:00","grupo":"A","mandante":"República Tcheca","visitante":"México"},
    {"id":"A06","data_hora":"2026-06-24 22:00","grupo":"A","mandante":"África do Sul","visitante":"Coreia do Sul"},

    # GRUPO B
    {"id":"B01","data_hora":"2026-06-12 16:00","grupo":"B","mandante":"Canadá","visitante":"Bósnia e Herzegovina"},
    {"id":"B02","data_hora":"2026-06-13 16:00","grupo":"B","mandante":"Catar","visitante":"Suíça"},
    {"id":"B03","data_hora":"2026-06-18 16:00","grupo":"B","mandante":"Suíça","visitante":"Bósnia e Herzegovina"},
    {"id":"B04","data_hora":"2026-06-18 19:00","grupo":"B","mandante":"Canadá","visitante":"Catar"},
    {"id":"B05","data_hora":"2026-06-24 16:00","grupo":"B","mandante":"Suíça","visitante":"Canadá"},
    {"id":"B06","data_hora":"2026-06-24 16:00","grupo":"B","mandante":"Bósnia e Herzegovina","visitante":"Catar"},

    # GRUPO C
    {"id":"C01","data_hora":"2026-06-13 19:00","grupo":"C","mandante":"Brasil","visitante":"Marrocos"},
    {"id":"C02","data_hora":"2026-06-13 22:00","grupo":"C","mandante":"Haiti","visitante":"Escócia"},
    {"id":"C03","data_hora":"2026-06-19 19:00","grupo":"C","mandante":"Escócia","visitante":"Marrocos"},
    {"id":"C04","data_hora":"2026-06-19 22:00","grupo":"C","mandante":"Brasil","visitante":"Haiti"},
    {"id":"C05","data_hora":"2026-06-24 19:00","grupo":"C","mandante":"Escócia","visitante":"Brasil"},
    {"id":"C06","data_hora":"2026-06-24 19:00","grupo":"C","mandante":"Marrocos","visitante":"Haiti"},

    # GRUPO D
    {"id":"D01","data_hora":"2026-06-12 22:00","grupo":"D","mandante":"Estados Unidos","visitante":"Paraguai"},
    {"id":"D02","data_hora":"2026-06-14 01:00","grupo":"D","mandante":"Austrália","visitante":"Turquia"},
    {"id":"D03","data_hora":"2026-06-19 16:00","grupo":"D","mandante":"Estados Unidos","visitante":"Austrália"},
    {"id":"D04","data_hora":"2026-06-20 01:00","grupo":"D","mandante":"Turquia","visitante":"Paraguai"},
    {"id":"D05","data_hora":"2026-06-25 23:00","grupo":"D","mandante":"Turquia","visitante":"Estados Unidos"},
    {"id":"D06","data_hora":"2026-06-25 23:00","grupo":"D","mandante":"Paraguai","visitante":"Austrália"},

    # GRUPO E
    {"id":"E01","data_hora":"2026-06-14 14:00","grupo":"E","mandante":"Alemanha","visitante":"Curaçao"},
    {"id":"E02","data_hora":"2026-06-14 20:00","grupo":"E","mandante":"Costa do Marfim","visitante":"Equador"},
    {"id":"E03","data_hora":"2026-06-20 17:00","grupo":"E","mandante":"Alemanha","visitante":"Costa do Marfim"},
    {"id":"E04","data_hora":"2026-06-20 17:00","grupo":"E","mandante":"Equador","visitante":"Curaçao"},
    {"id":"E05","data_hora":"2026-06-25 17:00","grupo":"E","mandante":"Equador","visitante":"Alemanha"},
    {"id":"E06","data_hora":"2026-06-25 17:00","grupo":"E","mandante":"Curaçao","visitante":"Costa do Marfim"},

    # GRUPO F
    {"id":"F01","data_hora":"2026-06-14 17:00","grupo":"F","mandante":"Holanda","visitante":"Japão"},
    {"id":"F02","data_hora":"2026-06-14 23:00","grupo":"F","mandante":"Suécia","visitante":"Tunísia"},
    {"id":"F03","data_hora":"2026-06-20 14:00","grupo":"F","mandante":"Holanda","visitante":"Suécia"},
    {"id":"F04","data_hora":"2026-06-21 01:00","grupo":"F","mandante":"Tunísia","visitante":"Japão"},
    {"id":"F05","data_hora":"2026-06-25 20:00","grupo":"F","mandante":"Japão","visitante":"Suécia"},
    {"id":"F06","data_hora":"2026-06-25 20:00","grupo":"F","mandante":"Tunísia","visitante":"Holanda"},

    # GRUPO G
    {"id":"G01","data_hora":"2026-06-15 16:00","grupo":"G","mandante":"Bélgica","visitante":"Egito"},
    {"id":"G02","data_hora":"2026-06-15 22:00","grupo":"G","mandante":"Irã","visitante":"Nova Zelândia"},
    {"id":"G03","data_hora":"2026-06-21 16:00","grupo":"G","mandante":"Bélgica","visitante":"Irã"},
    {"id":"G04","data_hora":"2026-06-21 22:00","grupo":"G","mandante":"Nova Zelândia","visitante":"Egito"},
    {"id":"G05","data_hora":"2026-06-27 00:00","grupo":"G","mandante":"Egito","visitante":"Irã"},
    {"id":"G06","data_hora":"2026-06-27 00:00","grupo":"G","mandante":"Nova Zelândia","visitante":"Bélgica"},

    # GRUPO H
    {"id":"H01","data_hora":"2026-06-15 13:00","grupo":"H","mandante":"Espanha","visitante":"Cabo Verde"},
    {"id":"H02","data_hora":"2026-06-15 19:00","grupo":"H","mandante":"Arábia Saudita","visitante":"Uruguai"},
    {"id":"H03","data_hora":"2026-06-21 13:00","grupo":"H","mandante":"Espanha","visitante":"Arábia Saudita"},
    {"id":"H04","data_hora":"2026-06-21 19:00","grupo":"H","mandante":"Uruguai","visitante":"Cabo Verde"},
    {"id":"H05","data_hora":"2026-06-26 21:00","grupo":"H","mandante":"Cabo Verde","visitante":"Arábia Saudita"},
    {"id":"H06","data_hora":"2026-06-26 21:00","grupo":"H","mandante":"Uruguai","visitante":"Espanha"},

    # GRUPO I
    {"id":"I01","data_hora":"2026-06-16 16:00","grupo":"I","mandante":"França","visitante":"Senegal"},
    {"id":"I02","data_hora":"2026-06-16 19:00","grupo":"I","mandante":"Iraque","visitante":"Noruega"},
    {"id":"I03","data_hora":"2026-06-22 16:00","grupo":"I","mandante":"França","visitante":"Iraque"},
    {"id":"I04","data_hora":"2026-06-22 18:00","grupo":"I","mandante":"Noruega","visitante":"Senegal"},
    {"id":"I05","data_hora":"2026-06-26 16:00","grupo":"I","mandante":"Noruega","visitante":"França"},
    {"id":"I06","data_hora":"2026-06-26 16:00","grupo":"I","mandante":"Senegal","visitante":"Iraque"},

    # GRUPO J
    {"id":"J01","data_hora":"2026-06-16 22:00","grupo":"J","mandante":"Argentina","visitante":"Argélia"},
    {"id":"J02","data_hora":"2026-06-17 01:00","grupo":"J","mandante":"Áustria","visitante":"Jordânia"},
    {"id":"J03","data_hora":"2026-06-22 14:00","grupo":"J","mandante":"Argentina","visitante":"Áustria"},
    {"id":"J04","data_hora":"2026-06-23 00:00","grupo":"J","mandante":"Jordânia","visitante":"Argélia"},
    {"id":"J05","data_hora":"2026-06-27 23:00","grupo":"J","mandante":"Argélia","visitante":"Áustria"},
    {"id":"J06","data_hora":"2026-06-27 23:00","grupo":"J","mandante":"Jordânia","visitante":"Argentina"},

    # GRUPO K
    {"id":"K01","data_hora":"2026-06-17 14:00","grupo":"K","mandante":"Portugal","visitante":"RD do Congo"},
    {"id":"K02","data_hora":"2026-06-17 23:00","grupo":"K","mandante":"Uzbequistão","visitante":"Colômbia"},
    {"id":"K03","data_hora":"2026-06-23 14:00","grupo":"K","mandante":"Portugal","visitante":"Uzbequistão"},
    {"id":"K04","data_hora":"2026-06-23 23:00","grupo":"K","mandante":"Colômbia","visitante":"RD do Congo"},
    {"id":"K05","data_hora":"2026-06-27 20:30","grupo":"K","mandante":"Colômbia","visitante":"Portugal"},
    {"id":"K06","data_hora":"2026-06-27 20:30","grupo":"K","mandante":"RD do Congo","visitante":"Uzbequistão"},

    # GRUPO L
    {"id":"L01","data_hora":"2026-06-17 17:00","grupo":"L","mandante":"Inglaterra","visitante":"Croácia"},
    {"id":"L02","data_hora":"2026-06-17 20:00","grupo":"L","mandante":"Gana","visitante":"Panamá"},
    {"id":"L03","data_hora":"2026-06-23 17:00","grupo":"L","mandante":"Inglaterra","visitante":"Gana"},
    {"id":"L04","data_hora":"2026-06-23 20:00","grupo":"L","mandante":"Panamá","visitante":"Croácia"},
    {"id":"L05","data_hora":"2026-06-27 18:00","grupo":"L","mandante":"Panamá","visitante":"Inglaterra"},
    {"id":"L06","data_hora":"2026-06-27 18:00","grupo":"L","mandante":"Croácia","visitante":"Gana"},
]


# ===================== MATA-MATA =====================
# Horários em America/Maceio (BRT). Os terceiros colocados precisam ser definidos
# quando a combinação oficial dos melhores terceiros sair. O admin pode preencher
# manualmente na tela "Configurar mata-mata".
MATA_MATA = [
    # 32 avos / fase de 32
    {"id":"M73", "fase":"32 avos", "data_hora":"2026-06-28 16:00", "estadio":"Los Angeles Stadium", "origem_mandante":{"tipo":"grupo", "grupo":"A", "pos":2, "label":"2º Grupo A", "confirmado":"África do Sul"}, "origem_visitante":{"tipo":"grupo", "grupo":"B", "pos":2, "label":"2º Grupo B", "confirmado":"Canadá"}},
    {"id":"M74", "fase":"32 avos", "data_hora":"2026-06-29 17:30", "estadio":"Boston Stadium", "origem_mandante":{"tipo":"grupo", "grupo":"E", "pos":1, "label":"1º Grupo E", "confirmado":"Alemanha"}, "origem_visitante":{"tipo":"terceiro", "grupos":"A/B/C/D/F", "label":"3º Grupo A/B/C/D/F"}},
    {"id":"M75", "fase":"32 avos", "data_hora":"2026-06-29 22:00", "estadio":"Guadalajara Stadium", "origem_mandante":{"tipo":"grupo", "grupo":"F", "pos":1, "label":"1º Grupo F"}, "origem_visitante":{"tipo":"grupo", "grupo":"C", "pos":2, "label":"2º Grupo C", "confirmado":"Marrocos"}},
    {"id":"M76", "fase":"32 avos", "data_hora":"2026-06-29 14:00", "estadio":"Houston Stadium", "origem_mandante":{"tipo":"grupo", "grupo":"C", "pos":1, "label":"1º Grupo C", "confirmado":"Brasil"}, "origem_visitante":{"tipo":"grupo", "grupo":"F", "pos":2, "label":"2º Grupo F"}},
    {"id":"M77", "fase":"32 avos", "data_hora":"2026-06-30 18:00", "estadio":"New York New Jersey Stadium", "origem_mandante":{"tipo":"grupo", "grupo":"I", "pos":1, "label":"1º Grupo I"}, "origem_visitante":{"tipo":"terceiro", "grupos":"C/D/F/G/H", "label":"3º Grupo C/D/F/G/H"}},
    {"id":"M78", "fase":"32 avos", "data_hora":"2026-06-30 14:00", "estadio":"Dallas Stadium", "origem_mandante":{"tipo":"grupo", "grupo":"E", "pos":2, "label":"2º Grupo E"}, "origem_visitante":{"tipo":"grupo", "grupo":"I", "pos":2, "label":"2º Grupo I"}},
    {"id":"M79", "fase":"32 avos", "data_hora":"2026-06-30 22:00", "estadio":"Mexico City Stadium", "origem_mandante":{"tipo":"grupo", "grupo":"A", "pos":1, "label":"1º Grupo A", "confirmado":"México"}, "origem_visitante":{"tipo":"terceiro", "grupos":"C/E/F/H/I", "label":"3º Grupo C/E/F/H/I"}},
    {"id":"M80", "fase":"32 avos", "data_hora":"2026-07-01 13:00", "estadio":"Atlanta Stadium", "origem_mandante":{"tipo":"grupo", "grupo":"L", "pos":1, "label":"1º Grupo L"}, "origem_visitante":{"tipo":"terceiro", "grupos":"E/H/I/J/K", "label":"3º Grupo E/H/I/J/K"}},
    {"id":"M81", "fase":"32 avos", "data_hora":"2026-07-01 21:00", "estadio":"San Francisco Bay Area Stadium", "origem_mandante":{"tipo":"grupo", "grupo":"D", "pos":1, "label":"1º Grupo D", "confirmado":"Estados Unidos"}, "origem_visitante":{"tipo":"terceiro", "grupos":"B/E/F/I/J", "label":"3º Grupo B/E/F/I/J"}},
    {"id":"M82", "fase":"32 avos", "data_hora":"2026-07-01 17:00", "estadio":"Seattle Stadium", "origem_mandante":{"tipo":"grupo", "grupo":"G", "pos":1, "label":"1º Grupo G"}, "origem_visitante":{"tipo":"terceiro", "grupos":"A/E/H/I/J", "label":"3º Grupo A/E/H/I/J"}},
    {"id":"M83", "fase":"32 avos", "data_hora":"2026-07-02 20:00", "estadio":"Toronto Stadium", "origem_mandante":{"tipo":"grupo", "grupo":"K", "pos":2, "label":"2º Grupo K"}, "origem_visitante":{"tipo":"grupo", "grupo":"L", "pos":2, "label":"2º Grupo L"}},
    {"id":"M84", "fase":"32 avos", "data_hora":"2026-07-02 16:00", "estadio":"Los Angeles Stadium", "origem_mandante":{"tipo":"grupo", "grupo":"H", "pos":1, "label":"1º Grupo H"}, "origem_visitante":{"tipo":"grupo", "grupo":"J", "pos":2, "label":"2º Grupo J"}},
    {"id":"M85", "fase":"32 avos", "data_hora":"2026-07-03 00:00", "estadio":"BC Place Vancouver", "origem_mandante":{"tipo":"grupo", "grupo":"B", "pos":1, "label":"1º Grupo B", "confirmado":"Suíça"}, "origem_visitante":{"tipo":"terceiro", "grupos":"E/F/G/I/J", "label":"3º Grupo E/F/G/I/J"}},
    {"id":"M86", "fase":"32 avos", "data_hora":"2026-07-03 19:00", "estadio":"Miami Stadium", "origem_mandante":{"tipo":"grupo", "grupo":"J", "pos":1, "label":"1º Grupo J", "confirmado":"Argentina"}, "origem_visitante":{"tipo":"grupo", "grupo":"H", "pos":2, "label":"2º Grupo H"}},
    {"id":"M87", "fase":"32 avos", "data_hora":"2026-07-03 22:30", "estadio":"Kansas City Stadium", "origem_mandante":{"tipo":"grupo", "grupo":"K", "pos":1, "label":"1º Grupo K"}, "origem_visitante":{"tipo":"terceiro", "grupos":"D/E/I/J/L", "label":"3º Grupo D/E/I/J/L"}},
    {"id":"M88", "fase":"32 avos", "data_hora":"2026-07-03 15:00", "estadio":"Dallas Stadium", "origem_mandante":{"tipo":"grupo", "grupo":"D", "pos":2, "label":"2º Grupo D"}, "origem_visitante":{"tipo":"grupo", "grupo":"G", "pos":2, "label":"2º Grupo G"}},

    # Oitavas
    {"id":"M89", "fase":"Oitavas", "data_hora":"2026-07-04 18:00", "estadio":"Philadelphia Stadium", "origem_mandante":{"tipo":"vencedor", "jogo":"M74", "label":"Vencedor M74"}, "origem_visitante":{"tipo":"vencedor", "jogo":"M77", "label":"Vencedor M77"}},
    {"id":"M90", "fase":"Oitavas", "data_hora":"2026-07-04 14:00", "estadio":"Houston Stadium", "origem_mandante":{"tipo":"vencedor", "jogo":"M73", "label":"Vencedor M73"}, "origem_visitante":{"tipo":"vencedor", "jogo":"M75", "label":"Vencedor M75"}},
    {"id":"M91", "fase":"Oitavas", "data_hora":"2026-07-05 17:00", "estadio":"New York New Jersey Stadium", "origem_mandante":{"tipo":"vencedor", "jogo":"M76", "label":"Vencedor M76"}, "origem_visitante":{"tipo":"vencedor", "jogo":"M78", "label":"Vencedor M78"}},
    {"id":"M92", "fase":"Oitavas", "data_hora":"2026-07-05 21:00", "estadio":"Mexico City Stadium", "origem_mandante":{"tipo":"vencedor", "jogo":"M79", "label":"Vencedor M79"}, "origem_visitante":{"tipo":"vencedor", "jogo":"M80", "label":"Vencedor M80"}},
    {"id":"M93", "fase":"Oitavas", "data_hora":"2026-07-06 16:00", "estadio":"Dallas Stadium", "origem_mandante":{"tipo":"vencedor", "jogo":"M83", "label":"Vencedor M83"}, "origem_visitante":{"tipo":"vencedor", "jogo":"M84", "label":"Vencedor M84"}},
    {"id":"M94", "fase":"Oitavas", "data_hora":"2026-07-06 21:00", "estadio":"Seattle Stadium", "origem_mandante":{"tipo":"vencedor", "jogo":"M81", "label":"Vencedor M81"}, "origem_visitante":{"tipo":"vencedor", "jogo":"M82", "label":"Vencedor M82"}},
    {"id":"M95", "fase":"Oitavas", "data_hora":"2026-07-07 13:00", "estadio":"Atlanta Stadium", "origem_mandante":{"tipo":"vencedor", "jogo":"M86", "label":"Vencedor M86"}, "origem_visitante":{"tipo":"vencedor", "jogo":"M88", "label":"Vencedor M88"}},
    {"id":"M96", "fase":"Oitavas", "data_hora":"2026-07-07 17:00", "estadio":"BC Place Vancouver", "origem_mandante":{"tipo":"vencedor", "jogo":"M85", "label":"Vencedor M85"}, "origem_visitante":{"tipo":"vencedor", "jogo":"M87", "label":"Vencedor M87"}},

    # Quartas, semifinal, terceiro lugar e final
    {"id":"M97", "fase":"Quartas", "data_hora":"2026-07-09 17:00", "estadio":"Boston Stadium", "origem_mandante":{"tipo":"vencedor", "jogo":"M89", "label":"Vencedor M89"}, "origem_visitante":{"tipo":"vencedor", "jogo":"M90", "label":"Vencedor M90"}},
    {"id":"M98", "fase":"Quartas", "data_hora":"2026-07-10 16:00", "estadio":"Los Angeles Stadium", "origem_mandante":{"tipo":"vencedor", "jogo":"M93", "label":"Vencedor M93"}, "origem_visitante":{"tipo":"vencedor", "jogo":"M94", "label":"Vencedor M94"}},
    {"id":"M99", "fase":"Quartas", "data_hora":"2026-07-11 18:00", "estadio":"Miami Stadium", "origem_mandante":{"tipo":"vencedor", "jogo":"M91", "label":"Vencedor M91"}, "origem_visitante":{"tipo":"vencedor", "jogo":"M92", "label":"Vencedor M92"}},
    {"id":"M100", "fase":"Quartas", "data_hora":"2026-07-11 22:00", "estadio":"Kansas City Stadium", "origem_mandante":{"tipo":"vencedor", "jogo":"M95", "label":"Vencedor M95"}, "origem_visitante":{"tipo":"vencedor", "jogo":"M96", "label":"Vencedor M96"}},
    {"id":"M101", "fase":"Semifinal", "data_hora":"2026-07-14 16:00", "estadio":"Dallas Stadium", "origem_mandante":{"tipo":"vencedor", "jogo":"M97", "label":"Vencedor M97"}, "origem_visitante":{"tipo":"vencedor", "jogo":"M98", "label":"Vencedor M98"}},
    {"id":"M102", "fase":"Semifinal", "data_hora":"2026-07-15 16:00", "estadio":"Atlanta Stadium", "origem_mandante":{"tipo":"vencedor", "jogo":"M99", "label":"Vencedor M99"}, "origem_visitante":{"tipo":"vencedor", "jogo":"M100", "label":"Vencedor M100"}},
    {"id":"M103", "fase":"Terceiro lugar", "data_hora":"2026-07-18 18:00", "estadio":"Miami Stadium", "origem_mandante":{"tipo":"perdedor", "jogo":"M101", "label":"Perdedor M101"}, "origem_visitante":{"tipo":"perdedor", "jogo":"M102", "label":"Perdedor M102"}},
    {"id":"M104", "fase":"Final", "data_hora":"2026-07-19 16:00", "estadio":"New York New Jersey Stadium", "origem_mandante":{"tipo":"vencedor", "jogo":"M101", "label":"Vencedor M101"}, "origem_visitante":{"tipo":"vencedor", "jogo":"M102", "label":"Vencedor M102"}},
]

ORDEM_FASES_MATA_MATA = ["32 avos", "Oitavas", "Quartas", "Semifinal", "Terceiro lugar", "Final"]

# ===================== BANDEIRAS =====================
BANDEIRAS_TIMES = {
    "México": "mx",
    "África do Sul": "za",
    "Coreia do Sul": "kr",
    "República Tcheca": "cz",
    "Canadá": "ca",
    "Bósnia e Herzegovina": "ba",
    "Catar": "qa",
    "Suíça": "ch",
    "Brasil": "br",
    "Marrocos": "ma",
    "Haiti": "ht",
    "Escócia": "gb-sct",
    "Estados Unidos": "us",
    "Paraguai": "py",
    "Austrália": "au",
    "Turquia": "tr",
    "Alemanha": "de",
    "Curaçao": "cw",
    "Costa do Marfim": "ci",
    "Equador": "ec",
    "Holanda": "nl",
    "Japão": "jp",
    "Suécia": "se",
    "Tunísia": "tn",
    "Bélgica": "be",
    "Egito": "eg",
    "Irã": "ir",
    "Nova Zelândia": "nz",
    "Espanha": "es",
    "Cabo Verde": "cv",
    "Arábia Saudita": "sa",
    "Uruguai": "uy",
    "França": "fr",
    "Senegal": "sn",
    "Iraque": "iq",
    "Noruega": "no",
    "Argentina": "ar",
    "Argélia": "dz",
    "Áustria": "at",
    "Jordânia": "jo",
    "Portugal": "pt",
    "RD do Congo": "cd",
    "Uzbequistão": "uz",
    "Colômbia": "co",
    "Inglaterra": "gb-eng",
    "Croácia": "hr",
    "Gana": "gh",
    "Panamá": "pa",
}


def time_com_bandeira(nome_time):
    nome_seguro = html.escape(nome_time or "")
    codigo = BANDEIRAS_TIMES.get(nome_time)

    if not codigo:
        return nome_seguro

    url = f"https://flagcdn.com/w40/{codigo}.png"
    return (
        "<span class='time-flag-wrap'>"
        f"<img class='flag-img' src='{url}' alt='Bandeira {nome_seguro}' loading='lazy'>"
        f"<span>{nome_seguro}</span>"
        "</span>"
    )


# ===================== ESTILO =====================
def aplicar_estilo():
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 1.5rem;
        max-width: 1500px;
    }

    h1, h2, h3 { letter-spacing: -0.4px; }

    div[data-testid="stInfo"] { border-radius: 10px; }

    .grupo-box {
        margin-top: 26px;
        margin-bottom: 8px;
        padding: 10px 14px;
        border-radius: 10px;
        background: #173b66;
        border-left: 6px solid #f97316;
        color: white;
        font-size: 24px;
        font-weight: 800;
    }

    .cabecalho-jogo {
        padding: 8px 10px;
        margin-top: 8px;
        margin-bottom: 4px;
        border-radius: 8px;
        background: #0f2747;
        color: #dbeafe;
        font-size: 13px;
        font-weight: 800;
        text-transform: uppercase;
    }

    .linha-jogo {
        padding: 8px 10px;
        margin-bottom: 4px;
        border-radius: 10px;
        background: #111827;
        border: 1px solid #243244;
    }

    .texto-data {
        color: #e5e7eb;
        font-weight: 700;
        font-size: 14px;
        white-space: nowrap;
    }

    .texto-time {
        color: #ffffff;
        font-weight: 700;
        font-size: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .time-flag-wrap {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        min-width: 0;
    }

    .flag-img {
        width: 30px;
        height: 20px;
        object-fit: cover;
        border-radius: 2px;
        border: 1px solid rgba(255,255,255,0.28);
        box-shadow: 0 0 0 1px rgba(0,0,0,0.18);
        flex: 0 0 auto;
    }

    .texto-x {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 55px;
        color: #60a5fa;
        font-weight: 900;
        text-align: center;
        font-size: 22px;
        line-height: 1;
    }

    .status-aberto {
        color: #22c55e;
        font-weight: 800;
        font-size: 14px;
        white-space: nowrap;
    }

    .status-fechado {
        color: #ef4444;
        font-weight: 800;
        font-size: 14px;
        white-space: nowrap;
    }

    div[data-testid="stNumberInput"] {
        max-width: 70px;
        margin: auto;
    }

    div[data-testid="stNumberInput"] input {
        text-align: center !important;
        font-weight: 800;
    }

    .stButton > button {
        border-radius: 10px;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)


# ===================== FIREBASE =====================
@st.cache_resource
def get_db():
    if not firebase_admin._apps:
        if "firebase_service_account" not in st.secrets:
            st.error("Configuração do Firebase não encontrada em st.secrets['firebase_service_account'].")
            st.stop()

        cred = credentials.Certificate(dict(st.secrets["firebase_service_account"]))
        firebase_admin.initialize_app(cred)

    try:
        return firestore.client(database_id="default")
    except TypeError:
        return firestore.client()


def now_iso():
    return datetime.now(TZ).isoformat()


def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    senha_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return salt, senha_hash


def check_password(password, salt, senha_hash):
    return hashlib.sha256((salt + password).encode()).hexdigest() == senha_hash


def normalize_user(usuario):
    return (usuario or "").strip().upper()


def doc_to_dict(doc):
    dados = doc.to_dict() or {}
    dados["id"] = doc.id
    return dados


def get_all_users():
    db = get_db()
    docs = db.collection("usuarios").stream()
    return {doc.id: doc.to_dict() or {} for doc in docs}


def get_user(usuario):
    db = get_db()
    usuario = normalize_user(usuario)
    snap = db.collection("usuarios").document(usuario).get()
    if snap.exists:
        return snap.to_dict() or {}
    return None


def save_user(usuario, dados, merge=True):
    db = get_db()
    usuario = normalize_user(usuario)
    db.collection("usuarios").document(usuario).set(dados, merge=merge)


def delete_user(usuario):
    db = get_db()
    usuario = normalize_user(usuario)
    db.collection("usuarios").document(usuario).delete()


def create_user(usuario, senha=SENHA_PADRAO, master=False, trocar_senha=False):
    usuario = normalize_user(usuario)
    salt, senha_hash = hash_password(senha)
    save_user(usuario, {
        "salt": salt,
        "senha_hash": senha_hash,
        "master": bool(master),
        "trocar_senha": bool(trocar_senha),
        "ativo": True,
        "criado_em": now_iso(),
        "atualizado_em": now_iso(),
    }, merge=False)


def reset_password(usuario):
    usuario = normalize_user(usuario)
    salt, senha_hash = hash_password(SENHA_PADRAO)
    save_user(usuario, {
        "salt": salt,
        "senha_hash": senha_hash,
        "trocar_senha": True,
        "atualizado_em": now_iso(),
        "senha_redefinida_em": now_iso(),
    }, merge=True)


def ensure_initial_users():
    users = get_all_users()

    if ADMIN_USER not in users:
        create_user(ADMIN_USER, SENHA_PADRAO, master=True, trocar_senha=False)

    for usuario in USUARIOS_INICIAIS:
        usuario = normalize_user(usuario)
        if usuario not in users:
            create_user(usuario, SENHA_PADRAO, master=False, trocar_senha=False)

    users = get_all_users()
    for usuario, dados in users.items():
        if dados.get("trocar_senha", False) and not dados.get("senha_redefinida_em"):
            save_user(usuario, {
                "trocar_senha": False,
                "atualizado_em": now_iso(),
                "migrado_troca_senha_primeiro_login": True,
            }, merge=True)


def get_palpites_usuario(usuario):
    db = get_db()
    usuario = normalize_user(usuario)
    doc = db.collection("palpites").document(usuario).get()
    return doc.to_dict() or {}


def save_palpites_usuario(usuario, palpites_usuario):
    db = get_db()
    usuario = normalize_user(usuario)
    db.collection("palpites").document(usuario).set(palpites_usuario)


def get_all_palpites():
    db = get_db()
    return {doc.id: doc.to_dict() or {} for doc in db.collection("palpites").stream()}


def delete_palpites_usuario(usuario):
    db = get_db()
    usuario = normalize_user(usuario)
    db.collection("palpites").document(usuario).delete()


def rename_palpites_usuario(usuario_antigo, novo_nome):
    db = get_db()
    usuario_antigo = normalize_user(usuario_antigo)
    novo_nome = normalize_user(novo_nome)
    dados = get_palpites_usuario(usuario_antigo)

    if dados:
        db.collection("palpites").document(novo_nome).set(dados)

    db.collection("palpites").document(usuario_antigo).delete()


def get_resultados():
    db = get_db()
    doc = db.collection("configuracoes").document("resultados_reais").get()
    return doc.to_dict() or {}


def save_resultados(resultados):
    db = get_db()
    db.collection("configuracoes").document("resultados_reais").set(resultados)


def get_mata_mata_manual():
    db = get_db()
    doc = db.collection("configuracoes").document("mata_mata_manual").get()
    return doc.to_dict() or {}


def save_mata_mata_manual(dados):
    db = get_db()
    db.collection("configuracoes").document("mata_mata_manual").set(dados)


# ===================== LOGIN =====================
def tela_trocar_senha(usuario, user_data):
    st.warning("Você precisa criar uma nova senha antes de continuar.")

    nova = st.text_input("Nova senha", type="password", key="nova_senha_obrigatoria")
    confirmar = st.text_input("Confirmar nova senha", type="password", key="confirma_senha_obrigatoria")

    if st.button("Salvar nova senha", use_container_width=True):
        if not nova or not confirmar:
            st.error("Preencha a nova senha e a confirmação.")
        elif nova != confirmar:
            st.error("As senhas não conferem.")
        elif len(nova) < 4:
            st.error("A senha precisa ter pelo menos 4 caracteres.")
        elif nova == SENHA_PADRAO:
            st.error("Escolha uma senha diferente da senha padrão 123.")
        else:
            salt, senha_hash = hash_password(nova)
            save_user(usuario, {
                "salt": salt,
                "senha_hash": senha_hash,
                "trocar_senha": False,
                "atualizado_em": now_iso(),
                "senha_alterada_em": now_iso(),
            }, merge=True)
            st.success("Senha alterada! Faça login novamente.")
            st.session_state.clear()
            st.rerun()

    st.stop()


def login_screen():
    aplicar_estilo()
    ensure_initial_users()

    st.title("🏆 Bolão Copa do Mundo 2026")

    tab_login, tab_criar = st.tabs(["Entrar", "Criar usuário"])

    with tab_login:
        with st.form("form_login"):
            usuario = normalize_user(st.text_input("Usuário", key="login_user"))
            senha = st.text_input("Senha", type="password", key="login_pass")
            entrar = st.form_submit_button("Entrar", use_container_width=True)

        if entrar:
            user_data = get_user(usuario)

            if not usuario or not senha:
                st.warning("Informe usuário e senha.")
            elif not user_data:
                st.error("Usuário ou senha inválidos.")
            elif not user_data.get("ativo", True):
                st.error("Usuário inativo. Fale com o admin.")
            elif check_password(senha, user_data.get("salt", ""), user_data.get("senha_hash", "")):
                st.session_state["usuario"] = usuario
                st.session_state["master"] = bool(user_data.get("master", False))
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")

    with tab_criar:
        novo_usuario = normalize_user(st.text_input("Novo usuário", key="criar_user"))
        nova_senha = st.text_input("Senha", type="password", key="criar_senha")
        confirmar_senha = st.text_input("Confirmar senha", type="password", key="criar_confirma_senha")

        if st.button("Criar usuário", use_container_width=True, key="btn_criar_usuario"):
            users = get_all_users()
            admin_name = ADMIN_USER.upper()

            if not novo_usuario or not nova_senha or not confirmar_senha:
                st.warning("Preencha usuário, senha e confirmação.")
            elif novo_usuario == admin_name:
                st.error("Esse nome é reservado para o admin.")
            elif novo_usuario in users:
                st.error("Esse usuário já existe.")
            elif nova_senha != confirmar_senha:
                st.error("As senhas não conferem.")
            elif len(nova_senha) < 3:
                st.error("A senha precisa ter pelo menos 3 caracteres.")
            else:
                create_user(novo_usuario, nova_senha, master=False, trocar_senha=False)
                st.success("Usuário criado! Agora faça login na aba Entrar.")


# ===================== REGRAS =====================
def resultado_tipo(gols_casa, gols_fora):
    if gols_casa > gols_fora:
        return "W"
    if gols_casa < gols_fora:
        return "L"
    return "D"


def valor_em_branco(valor):
    return valor is None or valor == "" or valor == "-"


def palpite_valido(palpite):
    if not isinstance(palpite, dict):
        return False

    if "casa" not in palpite or "fora" not in palpite:
        return False

    casa = palpite.get("casa")
    fora = palpite.get("fora")

    if valor_em_branco(casa) or valor_em_branco(fora):
        return False

    try:
        casa_int = int(casa)
        fora_int = int(fora)
    except Exception:
        return False

    if palpite.get("preenchido") is True:
        return True

    if casa_int == 0 and fora_int == 0:
        return False

    return True


def valor_palpite_para_tela(palpite, campo):
    if not isinstance(palpite, dict):
        return "-"

    if not palpite_valido(palpite):
        return "-"

    valor = palpite.get(campo)

    if valor_em_branco(valor):
        return "-"

    try:
        return int(valor)
    except Exception:
        return "-"


def seletor_gols(label, atual, campo, disabled, key):
    opcoes = ["-"] + list(range(0, 31))
    valor = valor_palpite_para_tela(atual, campo)
    indice = opcoes.index(valor) if valor in opcoes else 0

    return st.selectbox(
        label,
        opcoes,
        index=indice,
        disabled=disabled,
        key=key,
        label_visibility="collapsed",
        format_func=lambda x: "-" if x == "-" else str(x),
    )


def aplicar_palpite_temp(palpites_temp, jogo_id, casa, fora, extras=None):
    if casa == "-" or fora == "-":
        palpites_temp.pop(jogo_id, None)
        return

    dados = {
        "casa": int(casa),
        "fora": int(fora),
        "preenchido": True,
        "salvo_em": now_iso(),
    }

    if extras:
        dados.update(extras)

    palpites_temp[jogo_id] = dados


def calcula_pontos(palpite, real):
    if not palpite_valido(palpite) or real is None:
        return 0, "Pendente"

    pc, pf = int(palpite["casa"]), int(palpite["fora"])
    rc, rf = int(real["casa"]), int(real["fora"])

    if pc == rc and pf == rf:
        return 3, "Placar exato"

    if resultado_tipo(pc, pf) == resultado_tipo(rc, rf):
        return 1, "Resultado certo"

    return 0, "Errou"


def jogo_bloqueado(data_hora_str):
    inicio = datetime.strptime(data_hora_str, "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
    return datetime.now(TZ) >= inicio - timedelta(hours=LOCK_HOURS_BEFORE)


# ===================== CLASSIFICAÇÃO DOS GRUPOS / MATA-MATA =====================
def grupo_completo(resultados, grupo):
    jogos_grupo = [j for j in JOGOS if j["grupo"] == grupo]
    return all(j["id"] in resultados for j in jogos_grupo)


def classificacao_grupo_por_resultados(resultados, grupo):
    jogos_grupo = [j for j in JOGOS if j["grupo"] == grupo]
    times = sorted(set([j["mandante"] for j in jogos_grupo] + [j["visitante"] for j in jogos_grupo]))

    tabela = {
        time: {
            "time": time,
            "Pontos": 0,
            "Jogos": 0,
            "Vitórias": 0,
            "Empates": 0,
            "Derrotas": 0,
            "GP": 0,
            "GC": 0,
            "SG": 0,
        }
        for time in times
    }

    for j in jogos_grupo:
        r = resultados.get(j["id"])
        if not r:
            continue

        casa = int(r.get("casa", 0))
        fora = int(r.get("fora", 0))
        mandante = j["mandante"]
        visitante = j["visitante"]

        tabela[mandante]["Jogos"] += 1
        tabela[visitante]["Jogos"] += 1
        tabela[mandante]["GP"] += casa
        tabela[mandante]["GC"] += fora
        tabela[visitante]["GP"] += fora
        tabela[visitante]["GC"] += casa

        if casa > fora:
            tabela[mandante]["Pontos"] += 3
            tabela[mandante]["Vitórias"] += 1
            tabela[visitante]["Derrotas"] += 1
        elif casa < fora:
            tabela[visitante]["Pontos"] += 3
            tabela[visitante]["Vitórias"] += 1
            tabela[mandante]["Derrotas"] += 1
        else:
            tabela[mandante]["Pontos"] += 1
            tabela[visitante]["Pontos"] += 1
            tabela[mandante]["Empates"] += 1
            tabela[visitante]["Empates"] += 1

    for time in tabela:
        tabela[time]["SG"] = tabela[time]["GP"] - tabela[time]["GC"]

    return sorted(
        tabela.values(),
        key=lambda x: (-x["Pontos"], -x["SG"], -x["GP"], -x["Vitórias"], x["time"]),
    )


def todas_classificacoes_grupos(resultados):
    dados = {}
    for grupo in sorted(set(j["grupo"] for j in JOGOS)):
        if grupo_completo(resultados, grupo):
            dados[grupo] = classificacao_grupo_por_resultados(resultados, grupo)
    return dados


def eh_nome_placeholder(nome):
    nome = str(nome or "")
    prefixos = ("1º Grupo", "2º Grupo", "3º Grupo", "Vencedor", "Perdedor", "A definir")
    return nome.startswith(prefixos)


def vencedor_ou_perdedor_jogo(jogo_id, resultados, mata_mata_manual, retornar="vencedor", visitados=None):
    visitados = visitados or set()
    if jogo_id in visitados:
        return None

    visitados.add(jogo_id)
    resultado = resultados.get(jogo_id)

    if not resultado:
        return None

    jogo = next((j for j in resolver_mata_mata(resultados, mata_mata_manual, visitados) if j["id"] == jogo_id), None)
    if not jogo:
        return None

    mandante = jogo.get("mandante", "")
    visitante = jogo.get("visitante", "")

    if eh_nome_placeholder(mandante) or eh_nome_placeholder(visitante):
        return None

    casa = int(resultado.get("casa", 0))
    fora = int(resultado.get("fora", 0))
    vencedor_manual = resultado.get("vencedor")

    if casa > fora:
        vencedor = mandante
        perdedor = visitante
    elif casa < fora:
        vencedor = visitante
        perdedor = mandante
    elif vencedor_manual == mandante:
        vencedor = mandante
        perdedor = visitante
    elif vencedor_manual == visitante:
        vencedor = visitante
        perdedor = mandante
    else:
        return None

    return vencedor if retornar == "vencedor" else perdedor


def resolver_origem_mata_mata(origem, resultados, mata_mata_manual, visitados=None):
    classificacoes = todas_classificacoes_grupos(resultados)
    tipo = origem.get("tipo")

    if tipo == "grupo":
        grupo = origem.get("grupo")
        pos = int(origem.get("pos", 0))
        if grupo in classificacoes and len(classificacoes[grupo]) >= pos:
            return classificacoes[grupo][pos - 1]["time"]
        if origem.get("confirmado"):
            return origem.get("confirmado")
        return origem.get("label", "A definir")

    if tipo == "terceiro":
        if origem.get("confirmado"):
            return origem.get("confirmado")
        return origem.get("label", "3º melhor colocado")

    if tipo == "vencedor":
        nome = vencedor_ou_perdedor_jogo(origem.get("jogo"), resultados, mata_mata_manual, "vencedor", visitados)
        return nome or origem.get("label", f"Vencedor {origem.get('jogo')}")

    if tipo == "perdedor":
        nome = vencedor_ou_perdedor_jogo(origem.get("jogo"), resultados, mata_mata_manual, "perdedor", visitados)
        return nome or origem.get("label", f"Perdedor {origem.get('jogo')}")

    return origem.get("label", "A definir")


def resolver_mata_mata(resultados=None, mata_mata_manual=None, visitados=None):
    resultados = resultados or {}
    mata_mata_manual = mata_mata_manual or {}
    visitados = visitados or set()
    jogos_resolvidos = []

    for jogo in MATA_MATA:
        manual = mata_mata_manual.get(jogo["id"], {}) if isinstance(mata_mata_manual, dict) else {}
        mandante_manual = (manual.get("mandante") or "").strip()
        visitante_manual = (manual.get("visitante") or "").strip()

        mandante = mandante_manual or resolver_origem_mata_mata(jogo["origem_mandante"], resultados, mata_mata_manual, visitados)
        visitante = visitante_manual or resolver_origem_mata_mata(jogo["origem_visitante"], resultados, mata_mata_manual, visitados)

        item = dict(jogo)
        item["grupo"] = jogo["fase"]
        item["mandante"] = mandante
        item["visitante"] = visitante
        jogos_resolvidos.append(item)

    return jogos_resolvidos


def get_jogos_para_pontuar(resultados=None, mata_mata_manual=None):
    return JOGOS + resolver_mata_mata(resultados or {}, mata_mata_manual or {})


def validar_cadastro_fase_grupos():
    problemas = []
    grupos = sorted(set(j["grupo"] for j in JOGOS))

    if len(JOGOS) != 72:
        problemas.append(f"A fase de grupos deveria ter 72 jogos, mas o cadastro tem {len(JOGOS)}.")

    if len(grupos) != 12:
        problemas.append(f"A Copa deveria ter 12 grupos, mas o cadastro tem {len(grupos)} grupo(s): {', '.join(grupos)}.")

    for grupo in grupos:
        jogos_grupo = [j for j in JOGOS if j["grupo"] == grupo]
        if len(jogos_grupo) != 6:
            ids = ", ".join(j["id"] for j in jogos_grupo)
            problemas.append(f"Grupo {grupo} deveria ter 6 jogos, mas tem {len(jogos_grupo)}: {ids}")

    ids = [j["id"] for j in JOGOS]
    ids_repetidos = sorted({jogo_id for jogo_id in ids if ids.count(jogo_id) > 1})
    if ids_repetidos:
        problemas.append(f"Existem IDs repetidos na fase de grupos: {', '.join(ids_repetidos)}")

    return problemas


# ===================== RESUMO DE ACERTOS =====================
def texto_placar_palpite(palpite):
    if not palpite_valido(palpite):
        return "-"

    return f"{int(palpite['casa'])} x {int(palpite['fora'])}"


def texto_placar_real(real):
    if not real:
        return "-"

    return f"{int(real['casa'])} x {int(real['fora'])}"


def montar_resumo_acertos(usuario, palp_user, resultados, jogos_base=None):
    linhas = []
    jogos_base = jogos_base or JOGOS

    for j in jogos_base:
        palpite = palp_user.get(j["id"])
        real = resultados.get(j["id"])

        pontos, tipo_acerto = calcula_pontos(palpite, real)

        if pontos > 0:
            linhas.append({
                "Fase/Grupo": j.get("grupo", j.get("fase", "")),
                "Data": datetime.strptime(j["data_hora"], "%Y-%m-%d %H:%M").strftime("%d/%m/%Y %H:%M"),
                "Jogo": f"{j['mandante']} x {j['visitante']}",
                "Palpite": texto_placar_palpite(palpite),
                "Resultado real": texto_placar_real(real),
                "Acerto": tipo_acerto,
                "Pontos": pontos,
            })

    return pd.DataFrame(linhas)


def exibir_resumo_acertos(is_admin, usuario_logado, usuarios_validos, todos_palpites, resultados, jogos_base=None):
    st.divider()
    st.subheader("📋 Resumo dos acertos")

    if not resultados:
        st.info("Nenhum resultado real foi lançado ainda. Quando o admin lançar os resultados, os acertos aparecem aqui.")
        return

    if is_admin:
        st.info("Área do admin: você consegue ver o resumo de acertos de todos os usuários.")

        modo_resumo = st.radio(
            "Como deseja visualizar?",
            ["Todos os usuários", "Filtrar usuário"],
            horizontal=True,
            key="modo_resumo_acertos_admin",
        )

        if modo_resumo == "Filtrar usuário":
            usuario_escolhido = st.selectbox(
                "Selecione o usuário",
                usuarios_validos,
                key="usuario_resumo_acertos_admin",
            )

            palp_user = todos_palpites.get(usuario_escolhido, {})
            df_resumo = montar_resumo_acertos(usuario_escolhido, palp_user, resultados, jogos_base)

            st.markdown(f"### 👤 {usuario_escolhido}")

            if df_resumo.empty:
                st.warning("Esse usuário ainda não acertou nenhum jogo com resultado lançado.")
            else:
                total_pontos = int(df_resumo["Pontos"].sum())
                st.success(f"{usuario_escolhido} acertou {len(df_resumo)} jogo(s), somando {total_pontos} ponto(s).")
                st.dataframe(df_resumo, use_container_width=True, hide_index=True)

        else:
            for user in usuarios_validos:
                palp_user = todos_palpites.get(user, {})
                df_resumo = montar_resumo_acertos(user, palp_user, resultados, jogos_base)

                qtd_acertos = len(df_resumo)
                total_pontos = int(df_resumo["Pontos"].sum()) if not df_resumo.empty else 0

                with st.expander(f"{user} — {qtd_acertos} acerto(s) — {total_pontos} ponto(s)", expanded=False):
                    if df_resumo.empty:
                        st.warning("Nenhum acerto ainda.")
                    else:
                        st.dataframe(df_resumo, use_container_width=True, hide_index=True)

    else:
        palp_user = todos_palpites.get(usuario_logado, {})
        df_resumo = montar_resumo_acertos(usuario_logado, palp_user, resultados, jogos_base)

        st.info("Aqui aparecem somente os jogos que você acertou.")

        if df_resumo.empty:
            st.warning("Você ainda não acertou nenhum jogo com resultado lançado.")
        else:
            total_pontos = int(df_resumo["Pontos"].sum())
            st.success(f"Você acertou {len(df_resumo)} jogo(s), somando {total_pontos} ponto(s).")
            st.dataframe(df_resumo, use_container_width=True, hide_index=True)


# ===================== GERENCIAR USUÁRIOS =====================
def gerenciar_usuarios():
    st.subheader("👥 Gerenciar usuários")
    st.info("Área exclusiva do admin para alterar nomes, excluir participantes ou redefinir senha para 123.")

    users = get_all_users()
    admin_name = ADMIN_USER.upper()
    lista_usuarios = sorted([u for u in users.keys() if u != admin_name])

    if not lista_usuarios:
        st.warning("Nenhum usuário cadastrado ainda.")
        return

    st.markdown("### Usuários cadastrados")

    df_users = pd.DataFrame({
        "Usuário": lista_usuarios,
        "Trocar senha?": ["Sim" if users[u].get("trocar_senha", False) else "Não" for u in lista_usuarios],
        "Ativo?": ["Sim" if users[u].get("ativo", True) else "Não" for u in lista_usuarios],
    })

    st.dataframe(df_users, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### Alterar, excluir ou redefinir senha")

    usuario_antigo = st.selectbox("Selecione o usuário", lista_usuarios, key="admin_usuario_antigo")
    novo_nome = normalize_user(st.text_input("Novo nome", value=usuario_antigo, key="admin_novo_nome"))

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("✏️ Alterar nome", use_container_width=True):
            if not novo_nome:
                st.warning("Informe um novo nome válido.")
            elif novo_nome == admin_name:
                st.error("Esse nome é reservado para o admin.")
            elif novo_nome == usuario_antigo:
                st.warning("O novo nome é igual ao nome atual.")
            elif novo_nome in users:
                st.error("Já existe um usuário com esse nome.")
            else:
                dados_user = users[usuario_antigo]
                dados_user["alterado_em"] = now_iso()
                dados_user["nome_anterior"] = usuario_antigo

                save_user(novo_nome, dados_user, merge=False)
                delete_user(usuario_antigo)
                rename_palpites_usuario(usuario_antigo, novo_nome)

                st.success(f"Usuário alterado de {usuario_antigo} para {novo_nome}.")
                st.rerun()

    with col2:
        if st.button("🔑 Redefinir senha", use_container_width=True):
            reset_password(usuario_antigo)
            st.success(f"Senha de {usuario_antigo} redefinida para 123. No próximo login ele terá que criar uma nova senha.")
            st.rerun()

    with col3:
        if st.button("🗑️ Excluir usuário", use_container_width=True):
            delete_user(usuario_antigo)
            delete_palpites_usuario(usuario_antigo)
            st.success(f"Usuário {usuario_antigo} excluído.")
            st.rerun()

    st.divider()
    st.markdown("### Criar novo usuário manualmente")

    novo_usuario_manual = normalize_user(st.text_input("Nome do novo usuário", key="novo_usuario_manual"))
    senha_manual = st.text_input("Senha do novo usuário", type="password", key="senha_usuario_manual")
    confirma_senha_manual = st.text_input("Confirmar senha do novo usuário", type="password", key="confirma_senha_usuario_manual")

    if st.button("➕ Criar usuário", use_container_width=True, key="btn_criar_usuario_admin"):
        if not novo_usuario_manual or not senha_manual or not confirma_senha_manual:
            st.warning("Informe o nome do usuário, a senha e a confirmação.")
        elif novo_usuario_manual in users:
            st.error("Esse usuário já existe.")
        elif novo_usuario_manual == admin_name:
            st.error("Esse nome é reservado para o admin.")
        elif senha_manual != confirma_senha_manual:
            st.error("As senhas não conferem.")
        elif len(senha_manual) < 3:
            st.error("A senha precisa ter pelo menos 3 caracteres.")
        else:
            create_user(novo_usuario_manual, senha_manual, master=False, trocar_senha=False)
            st.success(f"Usuário {novo_usuario_manual} criado com a senha informada.")
            st.rerun()


# ===================== EDITAR PALPITES COMO ADMIN =====================
def editar_palpites_admin():
    st.subheader("🛠️ Editar palpites dos usuários")
    st.warning("Modo admin: todos os jogos ficam abertos para edição, mesmo os que já passaram ou travaram.")

    users = get_all_users()
    admin_name = ADMIN_USER.upper()
    lista_usuarios = sorted([u for u, d in users.items() if u != admin_name and d.get("ativo", True)])

    if not lista_usuarios:
        st.warning("Nenhum usuário disponível para editar.")
        return

    usuario_alvo = st.selectbox("Selecione o usuário para editar", lista_usuarios, key="admin_editar_palpites_usuario")
    palpites_temp = dict(get_palpites_usuario(usuario_alvo))

    st.markdown(f"### Editando palpites de: **{usuario_alvo}**")

    for grupo in sorted(set(j["grupo"] for j in JOGOS)):
        st.markdown(f"<div class='grupo-box'>Grupo {grupo}</div>", unsafe_allow_html=True)

        h1, h2, h3, h4, h5, h6, h7 = st.columns([1.4, 2.3, 0.55, 0.35, 0.55, 2.3, 0.9])
        h1.markdown("<div class='cabecalho-jogo'>Data/Hora</div>", unsafe_allow_html=True)
        h2.markdown("<div class='cabecalho-jogo'>Mandante</div>", unsafe_allow_html=True)
        h3.markdown("<div class='cabecalho-jogo'>Gols</div>", unsafe_allow_html=True)
        h4.markdown("<div class='cabecalho-jogo' style='text-align:center'>x</div>", unsafe_allow_html=True)
        h5.markdown("<div class='cabecalho-jogo'>Gols</div>", unsafe_allow_html=True)
        h6.markdown("<div class='cabecalho-jogo'>Visitante</div>", unsafe_allow_html=True)
        h7.markdown("<div class='cabecalho-jogo'>Status</div>", unsafe_allow_html=True)

        for j in [x for x in JOGOS if x["grupo"] == grupo]:
            atual = palpites_temp.get(j["id"], {})
            data_formatada = datetime.strptime(j["data_hora"], "%Y-%m-%d %H:%M").strftime("%d/%m/%Y - %H:%M")

            c1, c2, c3, c4, c5, c6, c7 = st.columns([1.4, 2.3, 0.55, 0.35, 0.55, 2.3, 0.9])

            with c1:
                st.markdown(f"<div class='linha-jogo texto-data'>{data_formatada}</div>", unsafe_allow_html=True)

            with c2:
                st.markdown(f"<div class='linha-jogo texto-time'>{time_com_bandeira(j['mandante'])}</div>", unsafe_allow_html=True)

            with c3:
                casa = seletor_gols(
                    "Gols mandante",
                    atual,
                    "casa",
                    disabled=False,
                    key=f"admin_edit_{usuario_alvo}_{j['id']}_c",
                )

            with c4:
                st.markdown("<div class='texto-x'>X</div>", unsafe_allow_html=True)

            with c5:
                fora = seletor_gols(
                    "Gols visitante",
                    atual,
                    "fora",
                    disabled=False,
                    key=f"admin_edit_{usuario_alvo}_{j['id']}_f",
                )

            with c6:
                st.markdown(f"<div class='linha-jogo texto-time'>{time_com_bandeira(j['visitante'])}</div>", unsafe_allow_html=True)

            with c7:
                st.markdown("<div class='linha-jogo status-aberto'>🔓 Admin</div>", unsafe_allow_html=True)

            aplicar_palpite_temp(
                palpites_temp,
                j["id"],
                casa,
                fora,
                extras={
                    "editado_por_admin": True,
                    "admin": st.session_state.get("usuario", ADMIN_USER),
                },
            )

    if st.button(f"Salvar palpites de {usuario_alvo}", use_container_width=True, key=f"salvar_palpites_admin_{usuario_alvo}"):
        save_palpites_usuario(usuario_alvo, palpites_temp)
        st.success(f"Palpites de {usuario_alvo} salvos no Firebase!")
        st.rerun()




# ===================== MATA-MATA UI =====================
def exibir_linhas_palpites(jogos, usuario, palpites_temp, prefixo_key, admin_liberado=False):
    for fase in ORDEM_FASES_MATA_MATA:
        jogos_fase = [j for j in jogos if j.get("fase") == fase]
        if not jogos_fase:
            continue

        st.markdown(f"<div class='grupo-box'>{fase}</div>", unsafe_allow_html=True)

        h1, h2, h3, h4, h5, h6, h7, h8 = st.columns([1.35, 0.9, 2.25, 0.55, 0.35, 0.55, 2.25, 0.9])
        h1.markdown("<div class='cabecalho-jogo'>Data/Hora</div>", unsafe_allow_html=True)
        h2.markdown("<div class='cabecalho-jogo'>Jogo</div>", unsafe_allow_html=True)
        h3.markdown("<div class='cabecalho-jogo'>Time 1</div>", unsafe_allow_html=True)
        h4.markdown("<div class='cabecalho-jogo'>Gols</div>", unsafe_allow_html=True)
        h5.markdown("<div class='cabecalho-jogo' style='text-align:center'>x</div>", unsafe_allow_html=True)
        h6.markdown("<div class='cabecalho-jogo'>Gols</div>", unsafe_allow_html=True)
        h7.markdown("<div class='cabecalho-jogo'>Time 2</div>", unsafe_allow_html=True)
        h8.markdown("<div class='cabecalho-jogo'>Status</div>", unsafe_allow_html=True)

        for j in jogos_fase:
            time_indefinido = eh_nome_placeholder(j.get("mandante")) or eh_nome_placeholder(j.get("visitante"))
            lock = False if admin_liberado else (jogo_bloqueado(j["data_hora"]) or time_indefinido)
            atual = palpites_temp.get(j["id"], {})
            data_formatada = datetime.strptime(j["data_hora"], "%Y-%m-%d %H:%M").strftime("%d/%m/%Y - %H:%M")

            c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1.35, 0.9, 2.25, 0.55, 0.35, 0.55, 2.25, 0.9])

            with c1:
                st.markdown(f"<div class='linha-jogo texto-data'>{data_formatada}</div>", unsafe_allow_html=True)

            with c2:
                st.markdown(f"<div class='linha-jogo texto-data'>{j['id']}</div>", unsafe_allow_html=True)

            with c3:
                st.markdown(f"<div class='linha-jogo texto-time'>{time_com_bandeira(j['mandante'])}</div>", unsafe_allow_html=True)

            with c4:
                casa = seletor_gols(
                    "Gols time 1",
                    atual,
                    "casa",
                    disabled=lock,
                    key=f"{prefixo_key}_{usuario}_{j['id']}_c"
                )

            with c5:
                st.markdown("<div class='texto-x'>X</div>", unsafe_allow_html=True)

            with c6:
                fora = seletor_gols(
                    "Gols time 2",
                    atual,
                    "fora",
                    disabled=lock,
                    key=f"{prefixo_key}_{usuario}_{j['id']}_f"
                )

            with c7:
                st.markdown(f"<div class='linha-jogo texto-time'>{time_com_bandeira(j['visitante'])}</div>", unsafe_allow_html=True)

            with c8:
                if time_indefinido and not admin_liberado:
                    st.markdown("<div class='linha-jogo status-fechado'>⏳ A definir</div>", unsafe_allow_html=True)
                elif lock:
                    st.markdown("<div class='linha-jogo status-fechado'>🔒 Fechado</div>", unsafe_allow_html=True)
                elif admin_liberado:
                    st.markdown("<div class='linha-jogo status-aberto'>🔓 Admin</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='linha-jogo status-aberto'>✅ Aberto</div>", unsafe_allow_html=True)

            if not lock:
                aplicar_palpite_temp(palpites_temp, j["id"], casa, fora)


def exibir_mata_mata(usuario, is_admin=False):
    st.subheader("🏆 Mata-mata")
    st.info("Os horários estão no fuso America/Maceio. Os jogos travam 1 hora antes do início, igual à fase de grupos.")

    resultados = get_resultados()
    mata_mata_manual = get_mata_mata_manual()
    jogos_mata_mata = resolver_mata_mata(resultados, mata_mata_manual)
    palpites_temp = dict(get_palpites_usuario(usuario))

    exibir_linhas_palpites(
        jogos=jogos_mata_mata,
        usuario=usuario,
        palpites_temp=palpites_temp,
        prefixo_key="mata",
        admin_liberado=False,
    )

    if st.button("Salvar meus palpites do mata-mata", use_container_width=True):
        save_palpites_usuario(usuario, palpites_temp)
        st.success("Palpites do mata-mata salvos no Firebase!")
        st.rerun()


def configurar_mata_mata_admin():
    st.subheader("🧩 Configurar mata-mata")
    st.info("Use essa tela para preencher manualmente os terceiros colocados ou corrigir algum time confirmado. Se deixar em branco, o sistema usa a classificação automática dos grupos/resultados já lançados e os confirmados do código.")

    resultados = get_resultados()
    mata_mata_manual = get_mata_mata_manual()
    jogos_mata_mata = resolver_mata_mata(resultados, mata_mata_manual)
    novo_manual = {}

    for fase in ORDEM_FASES_MATA_MATA:
        jogos_fase = [j for j in jogos_mata_mata if j.get("fase") == fase]
        if not jogos_fase:
            continue

        with st.expander(fase, expanded=(fase == "32 avos")):
            for j in jogos_fase:
                manual_atual = mata_mata_manual.get(j["id"], {}) if isinstance(mata_mata_manual, dict) else {}
                data_formatada = datetime.strptime(j["data_hora"], "%Y-%m-%d %H:%M").strftime("%d/%m/%Y %H:%M")
                st.markdown(f"**{j['id']} — {data_formatada} — {j.get('estadio', '')}**")

                c1, c2 = st.columns(2)
                with c1:
                    mandante = st.text_input(
                        "Time 1",
                        value=manual_atual.get("mandante", ""),
                        placeholder=j["mandante"],
                        key=f"manual_mm_{j['id']}_mandante",
                    ).strip()
                with c2:
                    visitante = st.text_input(
                        "Time 2",
                        value=manual_atual.get("visitante", ""),
                        placeholder=j["visitante"],
                        key=f"manual_mm_{j['id']}_visitante",
                    ).strip()

                if mandante or visitante:
                    novo_manual[j["id"]] = {}
                    if mandante:
                        novo_manual[j["id"]]["mandante"] = mandante
                    if visitante:
                        novo_manual[j["id"]]["visitante"] = visitante

                st.caption(f"Atual automático: {j['mandante']} x {j['visitante']}")
                st.divider()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Salvar configuração do mata-mata", use_container_width=True):
            save_mata_mata_manual(novo_manual)
            st.success("Configuração do mata-mata salva!")
            st.rerun()

    with c2:
        if st.button("Limpar configuração manual", use_container_width=True):
            save_mata_mata_manual({})
            st.success("Configuração manual limpa. O sistema voltará a usar a configuração automática.")
            st.rerun()


def exibir_resultados_mata_mata_admin(resultados_temp, resultados):
    st.markdown("### 🏆 Resultados reais — Mata-mata")
    st.info("Se um jogo de mata-mata terminar empatado no placar informado, selecione o vencedor para o sistema montar a próxima fase.")

    mata_mata_manual = get_mata_mata_manual()
    jogos_mata_mata = resolver_mata_mata(resultados_temp, mata_mata_manual)

    for fase in ORDEM_FASES_MATA_MATA:
        jogos_fase = [j for j in jogos_mata_mata if j.get("fase") == fase]
        if not jogos_fase:
            continue

        st.markdown(f"<div class='grupo-box'>{fase}</div>", unsafe_allow_html=True)

        h1, h2, h3, h4, h5, h6, h7, h8 = st.columns([1.35, 0.9, 2.25, 0.55, 0.35, 0.55, 2.25, 1.2])
        h1.markdown("<div class='cabecalho-jogo'>Data/Hora</div>", unsafe_allow_html=True)
        h2.markdown("<div class='cabecalho-jogo'>Jogo</div>", unsafe_allow_html=True)
        h3.markdown("<div class='cabecalho-jogo'>Time 1</div>", unsafe_allow_html=True)
        h4.markdown("<div class='cabecalho-jogo'>Gols</div>", unsafe_allow_html=True)
        h5.markdown("<div class='cabecalho-jogo' style='text-align:center'>x</div>", unsafe_allow_html=True)
        h6.markdown("<div class='cabecalho-jogo'>Gols</div>", unsafe_allow_html=True)
        h7.markdown("<div class='cabecalho-jogo'>Time 2</div>", unsafe_allow_html=True)
        h8.markdown("<div class='cabecalho-jogo'>Definido?</div>", unsafe_allow_html=True)

        for j in jogos_fase:
            atual = resultados.get(j["id"], {})
            ja_definido = j["id"] in resultados
            data_formatada = datetime.strptime(j["data_hora"], "%Y-%m-%d %H:%M").strftime("%d/%m/%Y - %H:%M")

            c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1.35, 0.9, 2.25, 0.55, 0.35, 0.55, 2.25, 1.2])

            with c1:
                st.markdown(f"<div class='linha-jogo texto-data'>{data_formatada}</div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='linha-jogo texto-data'>{j['id']}</div>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"<div class='linha-jogo texto-time'>{time_com_bandeira(j['mandante'])}</div>", unsafe_allow_html=True)
            with c4:
                casa = st.number_input("Gols time 1 real", min_value=0, max_value=30, value=int(atual.get("casa", 0)), key=f"real_{j['id']}_c", label_visibility="collapsed")
            with c5:
                st.markdown("<div class='texto-x'>X</div>", unsafe_allow_html=True)
            with c6:
                fora = st.number_input("Gols time 2 real", min_value=0, max_value=30, value=int(atual.get("fora", 0)), key=f"real_{j['id']}_f", label_visibility="collapsed")
            with c7:
                st.markdown(f"<div class='linha-jogo texto-time'>{time_com_bandeira(j['visitante'])}</div>", unsafe_allow_html=True)
            with c8:
                marcado = st.checkbox("OK", value=ja_definido, key=f"real_{j['id']}_check", label_visibility="collapsed")

            vencedor = atual.get("vencedor")
            if marcado and casa == fora and not eh_nome_placeholder(j["mandante"]) and not eh_nome_placeholder(j["visitante"]):
                vencedor = st.selectbox(
                    f"Vencedor nos pênaltis/prorrogação — {j['id']}",
                    [j["mandante"], j["visitante"]],
                    index=0 if atual.get("vencedor") != j["visitante"] else 1,
                    key=f"vencedor_{j['id']}",
                )

            if marcado:
                resultados_temp[j["id"]] = {"casa": casa, "fora": fora, "salvo_em": now_iso()}
                if vencedor:
                    resultados_temp[j["id"]]["vencedor"] = vencedor
            else:
                resultados_temp.pop(j["id"], None)

    return resultados_temp


# ===================== APP =====================
def app():
    aplicar_estilo()

    usuario = st.session_state["usuario"]
    user_data = get_user(usuario)

    if not user_data:
        st.session_state.clear()
        st.error("Usuário não encontrado. Faça login novamente.")
        st.stop()

    if user_data.get("trocar_senha", False):
        tela_trocar_senha(usuario, user_data)

    is_admin = bool(user_data.get("master", False)) or usuario == ADMIN_USER.upper()

    st.sidebar.success(f"Logado como: {usuario}")

    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()

    palpites_usuario = get_palpites_usuario(usuario)
    resultados = get_resultados()

    if is_admin:
        menu = st.sidebar.radio(
            "Menu",
            ["Meus palpites", "Mata-mata", "Editar palpites", "Classificação", "Resultados reais", "Configurar mata-mata", "Gerenciar usuários"]
        )
    else:
        menu = st.sidebar.radio(
            "Menu",
            ["Meus palpites", "Mata-mata", "Classificação", "Ver resultados"]
        )

    st.markdown("<h1 style='text-align:center'>🏆 BOLÃO DA COPA DO MUNDO 2026 🏆</h1>", unsafe_allow_html=True)

    if menu == "Meus palpites":
        st.subheader("Minha aba de palpites")
        st.info("Cada jogo trava automaticamente 1 hora antes do início.")

        st.markdown("""
        ### 📌 Regras de pontuação
        - **3 pontos**: acertou o placar exato.
        - **1 ponto**: acertou o resultado **W/D/L**: vitória do mandante, empate ou vitória do visitante.
        - **0 pontos**: errou o resultado.
        - **Sem pontuação**: se deixar `-`, fica como palpite não preenchido.
        """)

        palpites_temp = dict(palpites_usuario)

        for grupo in sorted(set(j["grupo"] for j in JOGOS)):
            st.markdown(f"<div class='grupo-box'>Grupo {grupo}</div>", unsafe_allow_html=True)

            h1, h2, h3, h4, h5, h6, h7 = st.columns([1.4, 2.3, 0.55, 0.35, 0.55, 2.3, 0.9])
            h1.markdown("<div class='cabecalho-jogo'>Data/Hora</div>", unsafe_allow_html=True)
            h2.markdown("<div class='cabecalho-jogo'>Mandante</div>", unsafe_allow_html=True)
            h3.markdown("<div class='cabecalho-jogo'>Gols</div>", unsafe_allow_html=True)
            h4.markdown("<div class='cabecalho-jogo' style='text-align:center'>x</div>", unsafe_allow_html=True)
            h5.markdown("<div class='cabecalho-jogo'>Gols</div>", unsafe_allow_html=True)
            h6.markdown("<div class='cabecalho-jogo'>Visitante</div>", unsafe_allow_html=True)
            h7.markdown("<div class='cabecalho-jogo'>Status</div>", unsafe_allow_html=True)

            for j in [x for x in JOGOS if x["grupo"] == grupo]:
                lock = jogo_bloqueado(j["data_hora"])
                atual = palpites_temp.get(j["id"], {})
                data_formatada = datetime.strptime(j["data_hora"], "%Y-%m-%d %H:%M").strftime("%d/%m/%Y - %H:%M")

                c1, c2, c3, c4, c5, c6, c7 = st.columns([1.4, 2.3, 0.55, 0.35, 0.55, 2.3, 0.9])

                with c1:
                    st.markdown(f"<div class='linha-jogo texto-data'>{data_formatada}</div>", unsafe_allow_html=True)

                with c2:
                    st.markdown(f"<div class='linha-jogo texto-time'>{time_com_bandeira(j['mandante'])}</div>", unsafe_allow_html=True)

                with c3:
                    casa = seletor_gols(
                        "Gols mandante",
                        atual,
                        "casa",
                        disabled=lock,
                        key=f"{usuario}_{j['id']}_c"
                    )

                with c4:
                    st.markdown("<div class='texto-x'>X</div>", unsafe_allow_html=True)

                with c5:
                    fora = seletor_gols(
                        "Gols visitante",
                        atual,
                        "fora",
                        disabled=lock,
                        key=f"{usuario}_{j['id']}_f"
                    )

                with c6:
                    st.markdown(f"<div class='linha-jogo texto-time'>{time_com_bandeira(j['visitante'])}</div>", unsafe_allow_html=True)

                with c7:
                    if lock:
                        st.markdown("<div class='linha-jogo status-fechado'>🔒 Fechado</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='linha-jogo status-aberto'>✅ Aberto</div>", unsafe_allow_html=True)

                if not lock:
                    aplicar_palpite_temp(palpites_temp, j["id"], casa, fora)

        if st.button("Salvar meus palpites", use_container_width=True):
            save_palpites_usuario(usuario, palpites_temp)
            st.success("Palpites salvos no Firebase!")
            st.rerun()

    elif menu == "Mata-mata":
        exibir_mata_mata(usuario, is_admin=is_admin)

    elif menu == "Editar palpites":
        if is_admin:
            editar_palpites_admin()
        else:
            st.error("Você não tem permissão para acessar esta área.")

    elif menu == "Classificação":
        st.subheader("🏅 Classificação")

        users = get_all_users()
        admin_name = ADMIN_USER.upper()
        usuarios_validos = sorted([u for u, d in users.items() if u != admin_name and d.get("ativo", True)])
        todos_palpites = get_all_palpites()
        mata_mata_manual = get_mata_mata_manual()
        jogos_pontuacao = get_jogos_para_pontuar(resultados, mata_mata_manual)

        linhas = []

        for user in usuarios_validos:
            palp_user = todos_palpites.get(user, {})
            pontos = 0
            exatos = 0
            resultados_certos = 0

            for j in jogos_pontuacao:
                p = palp_user.get(j["id"])
                r = resultados.get(j["id"])

                pts, desc = calcula_pontos(p, r)
                pontos += pts

                if desc == "Placar exato":
                    exatos += 1
                elif desc == "Resultado certo":
                    resultados_certos += 1

            linhas.append({
                "Participante": user,
                "Pontos": pontos,
                "Placares Exatos": exatos,
                "Resultados Certos": resultados_certos,
            })

        df = pd.DataFrame(linhas)

        if not df.empty:
            df = df.sort_values(
                ["Pontos", "Placares Exatos", "Resultados Certos", "Participante"],
                ascending=[False, False, False, True],
            ).reset_index(drop=True)

            df.insert(0, "Pos", df.index + 1)

            st.dataframe(df, use_container_width=True, hide_index=True)

            exibir_resumo_acertos(
                is_admin=is_admin,
                usuario_logado=usuario,
                usuarios_validos=usuarios_validos,
                todos_palpites=todos_palpites,
                resultados=resultados,
                jogos_base=jogos_pontuacao,
            )

        else:
            st.warning("Ainda não há usuários cadastrados para aparecer na classificação.")

    elif menu == "Configurar mata-mata":
        if is_admin:
            configurar_mata_mata_admin()
        else:
            st.error("Você não tem permissão para acessar esta área.")

    elif menu == "Gerenciar usuários":
        if is_admin:
            gerenciar_usuarios()
        else:
            st.error("Você não tem permissão para acessar esta área.")

    else:
        if is_admin:
            st.subheader("Lançar resultados reais")
            st.warning("Marque **Resultado definido** somente nos jogos que já terminaram. Jogo desmarcado não conta pontos na classificação.")

            problemas_cadastro = validar_cadastro_fase_grupos()
            if problemas_cadastro:
                st.error("⚠️ Atenção no cadastro dos jogos:\n" + "\n".join(f"- {p}" for p in problemas_cadastro))
            else:
                st.caption("✅ Fase de grupos cadastrada com 72 jogos: 12 grupos x 6 jogos. Grupo E inclui E05 — Equador x Alemanha e E06 — Curaçao x Costa do Marfim.")

            if st.button("🧹 Limpar todos os resultados reais", use_container_width=True):
                save_resultados({})
                st.success("Resultados reais limpos. A classificação foi zerada até você lançar novos resultados.")
                st.rerun()

            resultados_temp = dict(resultados)

            for grupo in sorted(set(j["grupo"] for j in JOGOS)):
                st.markdown(f"<div class='grupo-box'>Grupo {grupo}</div>", unsafe_allow_html=True)

                h1, h2, h3, h4, h5, h6, h7, h8 = st.columns([1.25, 0.6, 2.2, 0.55, 0.35, 0.55, 2.2, 1.2])
                h1.markdown("<div class='cabecalho-jogo'>Data/Hora</div>", unsafe_allow_html=True)
                h2.markdown("<div class='cabecalho-jogo'>ID</div>", unsafe_allow_html=True)
                h3.markdown("<div class='cabecalho-jogo'>Mandante</div>", unsafe_allow_html=True)
                h4.markdown("<div class='cabecalho-jogo'>Gols</div>", unsafe_allow_html=True)
                h5.markdown("<div class='cabecalho-jogo' style='text-align:center'>x</div>", unsafe_allow_html=True)
                h6.markdown("<div class='cabecalho-jogo'>Gols</div>", unsafe_allow_html=True)
                h7.markdown("<div class='cabecalho-jogo'>Visitante</div>", unsafe_allow_html=True)
                h8.markdown("<div class='cabecalho-jogo'>Definido?</div>", unsafe_allow_html=True)

                for j in sorted([x for x in JOGOS if x["grupo"] == grupo], key=lambda x: (x["data_hora"], x["id"])):
                    atual = resultados.get(j["id"], {})
                    ja_definido = j["id"] in resultados
                    data_formatada = datetime.strptime(j["data_hora"], "%Y-%m-%d %H:%M").strftime("%d/%m/%Y - %H:%M")

                    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1.25, 0.6, 2.2, 0.55, 0.35, 0.55, 2.2, 1.2])

                    with c1:
                        st.markdown(f"<div class='linha-jogo texto-data'>{data_formatada}</div>", unsafe_allow_html=True)

                    with c2:
                        st.markdown(f"<div class='linha-jogo texto-data'>{j['id']}</div>", unsafe_allow_html=True)

                    with c3:
                        st.markdown(f"<div class='linha-jogo texto-time'>{time_com_bandeira(j['mandante'])}</div>", unsafe_allow_html=True)

                    with c4:
                        casa = st.number_input(
                            "Gols mandante real",
                            min_value=0,
                            max_value=30,
                            value=int(atual.get("casa", 0)),
                            key=f"real_{j['id']}_c",
                            label_visibility="collapsed"
                        )

                    with c5:
                        st.markdown("<div class='texto-x'>X</div>", unsafe_allow_html=True)

                    with c6:
                        fora = st.number_input(
                            "Gols visitante real",
                            min_value=0,
                            max_value=30,
                            value=int(atual.get("fora", 0)),
                            key=f"real_{j['id']}_f",
                            label_visibility="collapsed"
                        )

                    with c7:
                        st.markdown(f"<div class='linha-jogo texto-time'>{time_com_bandeira(j['visitante'])}</div>", unsafe_allow_html=True)

                    with c8:
                        marcado = st.checkbox(
                            "OK",
                            value=ja_definido,
                            key=f"real_{j['id']}_check",
                            label_visibility="collapsed"
                        )

                    if marcado:
                        resultados_temp[j["id"]] = {
                            "casa": casa,
                            "fora": fora,
                            "salvo_em": now_iso()
                        }
                    else:
                        resultados_temp.pop(j["id"], None)

            st.divider()
            resultados_temp = exibir_resultados_mata_mata_admin(resultados_temp, resultados)

            if st.button("Salvar resultados reais", use_container_width=True):
                save_resultados(resultados_temp)
                st.success("Resultados reais salvos no Firebase!")
                st.rerun()

        else:
            st.subheader("Resultados reais")

            problemas_cadastro = validar_cadastro_fase_grupos()
            if problemas_cadastro:
                st.error("⚠️ Atenção no cadastro dos jogos:\n" + "\n".join(f"- {p}" for p in problemas_cadastro))

            linhas = []
            mata_mata_manual = get_mata_mata_manual()
            jogos_para_exibir = get_jogos_para_pontuar(resultados, mata_mata_manual)

            for j in jogos_para_exibir:
                r = resultados.get(j["id"])
                resultado_txt = "-" if not r else f"{r['casa']} x {r['fora']}"
                if r and r.get("vencedor"):
                    resultado_txt += f" — vencedor: {r['vencedor']}"

                data_obj = datetime.strptime(j["data_hora"], "%Y-%m-%d %H:%M")
                linhas.append({
                    "ID": j["id"],
                    "Data": data_obj.strftime("%d/%m/%Y %H:%M"),
                    "Fase/Grupo": j.get("grupo", j.get("fase", "")),
                    "Jogo": f"{j['mandante']} x {j['visitante']}",
                    "Resultado": resultado_txt,
                    "_ordem": data_obj,
                })

            df_resultados = pd.DataFrame(linhas)

            if not df_resultados.empty:
                df_resultados = df_resultados.sort_values(["_ordem", "ID"], ascending=[True, True]).drop(columns=["_ordem"])

                busca_resultado = st.text_input(
                    "Pesquisar por ID ou time",
                    placeholder="Ex.: E05, Equador, Alemanha",
                    key="busca_resultados_reais",
                ).strip().upper()

                if busca_resultado:
                    mascara = df_resultados.apply(
                        lambda linha: busca_resultado in " ".join(map(str, linha.values)).upper(),
                        axis=1,
                    )
                    df_resultados = df_resultados[mascara]

                st.dataframe(df_resultados, use_container_width=True, hide_index=True)
            else:
                st.warning("Nenhum jogo disponível para exibir.")


# ===================== MAIN =====================
st.set_page_config(page_title="Bolão Copa 2026", layout="wide")

if "usuario" not in st.session_state:
    login_screen()
else:
    app()
