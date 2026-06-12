"""Court-id -> extractor class registry."""

from __future__ import annotations

from .base import BaseExtractor
from .courts.ala import AlabamaSupreme
from .courts.alacivapp import AlabamaCivilAppeals
from .courts.alacrimapp import AlabamaCriminalAppeals
from .courts.alaska import AlaskaSupreme
from .courts.alaskactapp import AlaskaCourtOfAppeals
from .courts.ariz import ArizonaSupreme
from .courts.ark import ArkansasSupreme
from .courts.ca1 import FirstCircuit
from .courts.ca2 import SecondCircuit
from .courts.ca3 import ThirdCircuit
from .courts.ca4 import FourthCircuit
from .courts.ca5 import FifthCircuit
from .courts.ca6 import SixthCircuit
from .courts.ca7 import SeventhCircuit
from .courts.ca8 import EighthCircuit
from .courts.ca9 import NinthCircuit
from .courts.ca10 import TenthCircuit
from .courts.ca11 import EleventhCircuit
from .courts.cadc import DCCircuit
from .courts.cafc import FederalCircuit
from .courts.cal import CaliforniaSupreme
from .courts.calag import CaliforniaAttorneyGeneral
from .courts.calctapp import CaliforniaCourtOfAppeal
from .courts.delch import DelawareChancery
from .courts.scotus import SupremeCourtUS
from .courts.texbizct import TexasBusinessCourt
from .courts.mdag import MarylandAttorneyGeneral
from .courts.acca import ArmyCCA
from .courts.afcca import AirForceCCA
from .courts.nmcca import NavyMarineCCA
from .courts.uscgcoca import CoastGuardCCA
from .courts.armfor import ArmedForcesCourt
from .courts.indtc import IndianaTaxCourt
from .courts.minnag import MinnesotaAttorneyGeneral
from .courts.texag import TexasAttorneyGeneral
from .courts.delctcompl import DelawareCommonPleas
from .courts.conn import ConnecticutSupreme
from .courts.dc import DCCourtOfAppeals
from .courts.delaware import DelawareSupreme
from .courts.fla import FloridaSupreme
from .courts.ga import GeorgiaSupreme
from .courts.generic import GenericExtractor  # noqa: F401
from .courts.haw import HawaiiSupreme
from .courts.idaho import IdahoSupreme
from .courts.ill import IllinoisSupreme
from .courts.ind import IndianaSupreme
from .courts.iowa import IowaSupreme
from .courts.kan import KansasSupreme
from .courts.ky import KentuckySupreme
from .courts.la import LouisianaSupreme
from .courts.mass import MassachusettsSupreme
from .courts.md import MarylandSupreme
from .courts.me import MaineSupreme
from .courts.mich import MichiganSupreme
from .courts.minn import MinnesotaSupreme
from .courts.miss import MississippiSupreme
from .courts.mo import MissouriSupreme
from .courts.mont import MontanaSupreme
from .courts.nc import NorthCarolinaSupreme
from .courts.neb import NebraskaSupreme
from .courts.nev import NevadaSupreme
from .courts.nh import NewHampshireSupreme
from .courts.nj import NewJerseySupreme
from .courts.nm import NewMexicoSupreme
from .courts.ohio import OhioSupreme
from .courts.oregon import OregonSupreme
from .courts.pa import PennsylvaniaSupreme
from .courts.ri import RhodeIslandSupreme
from .courts.sc import SouthCarolinaSupreme
from .courts.sd import SouthDakotaSupreme
from .courts.prsupreme import PuertoRicoSupreme
from .courts.asbca import ArmedServicesBCA
from .courts.bia import BoardOfImmigrationAppeals
from .courts.mspb import MeritSystemsProtectionBoard
from .courts.ttab import TrademarkBoard
from .courts.olc import OfficeOfLegalCounsel
from .courts.ohioctcl import OhioCourtOfClaims
from .courts.ortc import OregonTaxMagistrate
from .courts.tax import USTaxCourt
from .courts.cit import CourtOfInternationalTrade
from .courts.uscfc import CourtOfFederalClaims
from .courts.cavc import VeteransClaimsCourt
from .courts.bap6 import SixthCircuitBAP
from .courts.guam import GuamSupreme
from .courts.nmariana import NorthernMarianaSupreme
from .courts.njtaxct import NewJerseyTaxCourt
from .courts.pacommwct import PennsylvaniaCommonwealthCourt
from .courts.tenn import TennesseeSupreme
from .courts.tex import TexasSupreme
from .courts.utah import UtahSupreme
from .courts.va import VirginiaSupreme
from .courts.vt import VermontSupreme
from .courts.wash import WashingtonSupreme
from .courts.wis import WisconsinSupreme
from .courts.wva import WestVirginiaSupreme
from .courts.wyo import WyomingSupreme

# --- U.S. district courts ---
from .courts.akd import DistrictOfAlaska
from .courts.almd import MiddleDistrictOfAlabama
from .courts.alnd import NorthernDistrictOfAlabama
from .courts.alsd import SouthernDistrictOfAlabama
from .courts.ared import EasternDistrictOfArkansas
from .courts.arwd import WesternDistrictOfArkansas
from .courts.azd import DistrictOfArizona
from .courts.cacd import CentralDistrictOfCalifornia
from .courts.caed import EasternDistrictOfCalifornia
from .courts.cand import NorthernDistrictOfCalifornia
from .courts.casd import SouthernDistrictOfCalifornia
from .courts.cod import DistrictOfColorado
from .courts.ctd import DistrictOfConnecticut
from .courts.dcd import DistrictOfColumbia
from .courts.ded import DistrictOfDelaware
from .courts.flmd import MiddleDistrictOfFlorida
from .courts.flnd import NorthernDistrictOfFlorida
from .courts.flsd import SouthernDistrictOfFlorida
from .courts.gamd import MiddleDistrictOfGeorgia
from .courts.gand import NorthernDistrictOfGeorgia
from .courts.gasd import SouthernDistrictOfGeorgia
from .courts.hid import DistrictOfHawaii
from .courts.iand import NorthernDistrictOfIowa
from .courts.iasd import SouthernDistrictOfIowa
from .courts.idd import DistrictOfIdaho
from .courts.ilcd import CentralDistrictOfIllinois
from .courts.ilnd import NorthernDistrictOfIllinois
from .courts.ilsd import SouthernDistrictOfIllinois
from .courts.innd import NorthernDistrictOfIndiana
from .courts.insd import SouthernDistrictOfIndiana
from .courts.ksd import DistrictOfKansas
from .courts.kyed import EasternDistrictOfKentucky
from .courts.kywd import WesternDistrictOfKentucky
from .courts.laed import EasternDistrictOfLouisiana
from .courts.lamd import MiddleDistrictOfLouisiana
from .courts.lawd import WesternDistrictOfLouisiana
from .courts.mad import DistrictOfMassachusetts
from .courts.mdd import DistrictOfMaryland
from .courts.med import DistrictOfMaine
from .courts.mied import EasternDistrictOfMichigan
from .courts.miwd import WesternDistrictOfMichigan
from .courts.mnd import DistrictOfMinnesota
from .courts.moed import EasternDistrictOfMissouri
from .courts.mowd import WesternDistrictOfMissouri
from .courts.msnd import NorthernDistrictOfMississippi
from .courts.mssd import SouthernDistrictOfMississippi
from .courts.mtd import DistrictOfMontana
from .courts.nced import EasternDistrictOfNorthCarolina
from .courts.ncmd import MiddleDistrictOfNorthCarolina
from .courts.ncwd import WesternDistrictOfNorthCarolina
from .courts.nd import NorthDakotaSupreme
from .courts.ndd import DistrictOfNorthDakota
from .courts.ned import DistrictOfNebraska
from .courts.nhd import DistrictOfNewHampshire
from .courts.njd import DistrictOfNewJersey
from .courts.nmd import DistrictOfNewMexico
from .courts.nvd import DistrictOfNevada
from .courts.nycivct import NewYorkCivilCourt
from .courts.nyfamct import NewYorkFamilyCourt
from .courts.nysupct import NewYorkSupremeCourt
from .courts.nysurct import NewYorkSurrogatesCourt
from .courts.nyed import EasternDistrictOfNewYork
from .courts.nynd import NorthernDistrictOfNewYork
from .courts.nysd import SouthernDistrictOfNewYork
from .courts.nywd import WesternDistrictOfNewYork
from .courts.ohnd import NorthernDistrictOfOhio
from .courts.ohsd import SouthernDistrictOfOhio
from .courts.oked import EasternDistrictOfOklahoma
from .courts.oknd import NorthernDistrictOfOklahoma
from .courts.okwd import WesternDistrictOfOklahoma
from .courts.ord import DistrictOfOregon
from .courts.paed import EasternDistrictOfPennsylvania
from .courts.pamd import MiddleDistrictOfPennsylvania
from .courts.pawd import WesternDistrictOfPennsylvania
from .courts.rid import DistrictOfRhodeIsland
from .courts.scd import DistrictOfSouthCarolina
from .courts.sdd import DistrictOfSouthDakota
from .courts.tned import EasternDistrictOfTennessee
from .courts.tnmd import MiddleDistrictOfTennessee
from .courts.tnwd import WesternDistrictOfTennessee
from .courts.txed import EasternDistrictOfTexas
from .courts.txnd import NorthernDistrictOfTexas
from .courts.txsd import SouthernDistrictOfTexas
from .courts.txwd import WesternDistrictOfTexas
from .courts.utd import DistrictOfUtah
from .courts.vaed import EasternDistrictOfVirginia
from .courts.vawd import WesternDistrictOfVirginia
from .courts.vtd import DistrictOfVermont
from .courts.waed import EasternDistrictOfWashington
from .courts.wawd import WesternDistrictOfWashington
from .courts.wied import EasternDistrictOfWisconsin
from .courts.wiwd import WesternDistrictOfWisconsin
from .courts.wvnd import NorthernDistrictOfWestVirginia
from .courts.wvsd import SouthernDistrictOfWestVirginia
from .courts.wyd import DistrictOfWyoming

# --- state intermediate appellate courts ---
from .courts.arizctapp import ArizonaCourtOfAppeals
from .courts.arkctapp import ArkansasCourtOfAppeals
from .courts.coloctapp import ColoradoCourtOfAppeals
from .courts.connappct import ConnecticutAppellateCourt
from .courts.delsuperct import DelawareSuperiorCourt
from .courts.fladistctapp import FloridaDistrictCourtOfAppeal
from .courts.gactapp import CourtOfAppealsOfGeorgia
from .courts.hawapp import IntermediateCourtOfAppealsOfHawaii
from .courts.idahoctapp import IdahoCourtOfAppeals
from .courts.illappct import IllinoisAppellateCourt
from .courts.indctapp import CourtOfAppealsOfIndiana
from .courts.iowactapp import IowaCourtOfAppeals
from .courts.kanctapp import KansasCourtOfAppeals
from .courts.kyctapp import KentuckyCourtOfAppeals
from .courts.lactapp import LouisianaCourtOfAppeal
from .courts.massappct import MassachusettsAppealsCourt
from .courts.mesuperct import MaineSuperiorCourt
from .courts.michctapp import MichiganCourtOfAppeals
from .courts.minnctapp import MinnesotaCourtOfAppeals
from .courts.missctapp import MississippiCourtOfAppeals
from .courts.moctapp import MissouriCourtOfAppeals
from .courts.ncctapp import NorthCarolinaCourtOfAppeals
from .courts.nebctapp import NebraskaCourtOfAppeals
from .courts.nevapp import NevadaCourtOfAppeals
from .courts.nmctapp import NewMexicoCourtOfAppeals
from .courts.ohioctapp import OhioCourtOfAppeals
from .courts.orctapp import OregonCourtOfAppeals
from .courts.pasuperct import PennsylvaniaSuperiorCourt
from .courts.prapp import PuertoRicoCourtOfAppeals
from .courts.scctapp import SouthCarolinaCourtOfAppeals
from .courts.tenncrimapp import TennesseeCourtOfCriminalAppeals
from .courts.tennctapp import TennesseeCourtOfAppeals
from .courts.texapp import TexasCourtOfAppeals
from .courts.texcrimapp import TexasCourtOfCriminalAppeals
from .courts.vactapp import CourtOfAppealsOfVirginia
from .courts.vtsuperct import VermontSuperiorCourt
from .courts.washctapp import WashingtonCourtOfAppeals
from .courts.wisctapp import WisconsinCourtOfAppeals
from .courts.wvactapp import IntermediateCourtOfAppealsOfWestVirginia
from .courts.mdctspecapp import AppellateCourtOfMaryland
from .courts.njsuperctappdiv import NewJerseySuperiorCourtAppellateDivision
from .courts.utahctapp import UtahCourtOfAppeals


EXTRACTORS: dict[str, type[BaseExtractor]] = {
    "ala": AlabamaSupreme,
    "alacivapp": AlabamaCivilAppeals,
    "alacrimapp": AlabamaCriminalAppeals,
    "alaska": AlaskaSupreme,
    "alaskactapp": AlaskaCourtOfAppeals,
    "ariz": ArizonaSupreme,
    "ark": ArkansasSupreme,
    "ca1": FirstCircuit,
    "ca2": SecondCircuit,
    "ca3": ThirdCircuit,
    "ca4": FourthCircuit,
    "ca5": FifthCircuit,
    "ca6": SixthCircuit,
    "ca7": SeventhCircuit,
    "ca8": EighthCircuit,
    "ca9": NinthCircuit,
    "ca10": TenthCircuit,
    "ca11": EleventhCircuit,
    "cadc": DCCircuit,
    "cafc": FederalCircuit,
    "cal": CaliforniaSupreme,
    "calag": CaliforniaAttorneyGeneral,
    "calctapp": CaliforniaCourtOfAppeal,
    "conn": ConnecticutSupreme,
    "dc": DCCourtOfAppeals,
    "del": DelawareSupreme,
    "delch": DelawareChancery,
    "delctcompl": DelawareCommonPleas,
    "fla": FloridaSupreme,
    "ga": GeorgiaSupreme,
    "haw": HawaiiSupreme,
    "idaho": IdahoSupreme,
    "ill": IllinoisSupreme,
    "ind": IndianaSupreme,
    "iowa": IowaSupreme,
    "kan": KansasSupreme,
    "ky": KentuckySupreme,
    "la": LouisianaSupreme,
    "mass": MassachusettsSupreme,
    "md": MarylandSupreme,
    "me": MaineSupreme,
    "mich": MichiganSupreme,
    "minn": MinnesotaSupreme,
    "miss": MississippiSupreme,
    "mo": MissouriSupreme,
    "mont": MontanaSupreme,
    "nc": NorthCarolinaSupreme,
    "neb": NebraskaSupreme,
    "nev": NevadaSupreme,
    "nh": NewHampshireSupreme,
    "nj": NewJerseySupreme,
    "nm": NewMexicoSupreme,
    "ohio": OhioSupreme,
    "or": OregonSupreme,
    "pa": PennsylvaniaSupreme,
    "ri": RhodeIslandSupreme,
    "sc": SouthCarolinaSupreme,
    "prsupreme": PuertoRicoSupreme,
    "asbca": ArmedServicesBCA,
    "bia": BoardOfImmigrationAppeals,
    "mspb": MeritSystemsProtectionBoard,
    "ttab": TrademarkBoard,
    "olc": OfficeOfLegalCounsel,
    "ohioctcl": OhioCourtOfClaims,
    "ortc": OregonTaxMagistrate,
    "tax": USTaxCourt,
    "cit": CourtOfInternationalTrade,
    "uscfc": CourtOfFederalClaims,
    "cavc": VeteransClaimsCourt,
    "bap6": SixthCircuitBAP,
    "guam": GuamSupreme,
    "nmariana": NorthernMarianaSupreme,
    "njtaxct": NewJerseyTaxCourt,
    "pacommwct": PennsylvaniaCommonwealthCourt,
    "sd": SouthDakotaSupreme,
    "scotus": SupremeCourtUS,
    "texbizct": TexasBusinessCourt,
    "mdag": MarylandAttorneyGeneral,
    "acca": ArmyCCA,
    "afcca": AirForceCCA,
    "nmcca": NavyMarineCCA,
    "uscgcoca": CoastGuardCCA,
    "armfor": ArmedForcesCourt,
    "indtc": IndianaTaxCourt,
    "minnag": MinnesotaAttorneyGeneral,
    "texag": TexasAttorneyGeneral,
    "tenn": TennesseeSupreme,
    "tex": TexasSupreme,
    "utah": UtahSupreme,
    "va": VirginiaSupreme,
    "vt": VermontSupreme,
    "wash": WashingtonSupreme,
    "wis": WisconsinSupreme,
    "wva": WestVirginiaSupreme,
    "wyo": WyomingSupreme,
    # --- U.S. district courts ---
    "akd": DistrictOfAlaska,
    "almd": MiddleDistrictOfAlabama,
    "alnd": NorthernDistrictOfAlabama,
    "alsd": SouthernDistrictOfAlabama,
    "ared": EasternDistrictOfArkansas,
    "arwd": WesternDistrictOfArkansas,
    "azd": DistrictOfArizona,
    "cacd": CentralDistrictOfCalifornia,
    "caed": EasternDistrictOfCalifornia,
    "cand": NorthernDistrictOfCalifornia,
    "casd": SouthernDistrictOfCalifornia,
    "cod": DistrictOfColorado,
    "ctd": DistrictOfConnecticut,
    "dcd": DistrictOfColumbia,
    "ded": DistrictOfDelaware,
    "flmd": MiddleDistrictOfFlorida,
    "flnd": NorthernDistrictOfFlorida,
    "flsd": SouthernDistrictOfFlorida,
    "gamd": MiddleDistrictOfGeorgia,
    "gand": NorthernDistrictOfGeorgia,
    "gasd": SouthernDistrictOfGeorgia,
    "hid": DistrictOfHawaii,
    "iand": NorthernDistrictOfIowa,
    "iasd": SouthernDistrictOfIowa,
    "idd": DistrictOfIdaho,
    "ilcd": CentralDistrictOfIllinois,
    "ilnd": NorthernDistrictOfIllinois,
    "ilsd": SouthernDistrictOfIllinois,
    "innd": NorthernDistrictOfIndiana,
    "insd": SouthernDistrictOfIndiana,
    "ksd": DistrictOfKansas,
    "kyed": EasternDistrictOfKentucky,
    "kywd": WesternDistrictOfKentucky,
    "laed": EasternDistrictOfLouisiana,
    "lamd": MiddleDistrictOfLouisiana,
    "lawd": WesternDistrictOfLouisiana,
    "mad": DistrictOfMassachusetts,
    "mdd": DistrictOfMaryland,
    "med": DistrictOfMaine,
    "mied": EasternDistrictOfMichigan,
    "miwd": WesternDistrictOfMichigan,
    "mnd": DistrictOfMinnesota,
    "moed": EasternDistrictOfMissouri,
    "mowd": WesternDistrictOfMissouri,
    "msnd": NorthernDistrictOfMississippi,
    "mssd": SouthernDistrictOfMississippi,
    "mtd": DistrictOfMontana,
    "nced": EasternDistrictOfNorthCarolina,
    "ncmd": MiddleDistrictOfNorthCarolina,
    "ncwd": WesternDistrictOfNorthCarolina,
    "nd": NorthDakotaSupreme,
    "ndd": DistrictOfNorthDakota,
    "ned": DistrictOfNebraska,
    "nhd": DistrictOfNewHampshire,
    "njd": DistrictOfNewJersey,
    "nmd": DistrictOfNewMexico,
    "nvd": DistrictOfNevada,
    "nycivct": NewYorkCivilCourt,
    "nyfamct": NewYorkFamilyCourt,
    "nysupct": NewYorkSupremeCourt,
    "nysurct": NewYorkSurrogatesCourt,
    "nyed": EasternDistrictOfNewYork,
    "nynd": NorthernDistrictOfNewYork,
    "nysd": SouthernDistrictOfNewYork,
    "nywd": WesternDistrictOfNewYork,
    "ohnd": NorthernDistrictOfOhio,
    "ohsd": SouthernDistrictOfOhio,
    "oked": EasternDistrictOfOklahoma,
    "oknd": NorthernDistrictOfOklahoma,
    "okwd": WesternDistrictOfOklahoma,
    "ord": DistrictOfOregon,
    "paed": EasternDistrictOfPennsylvania,
    "pamd": MiddleDistrictOfPennsylvania,
    "pawd": WesternDistrictOfPennsylvania,
    "rid": DistrictOfRhodeIsland,
    "scd": DistrictOfSouthCarolina,
    "sdd": DistrictOfSouthDakota,
    "tned": EasternDistrictOfTennessee,
    "tnmd": MiddleDistrictOfTennessee,
    "tnwd": WesternDistrictOfTennessee,
    "txed": EasternDistrictOfTexas,
    "txnd": NorthernDistrictOfTexas,
    "txsd": SouthernDistrictOfTexas,
    "txwd": WesternDistrictOfTexas,
    "utd": DistrictOfUtah,
    "vaed": EasternDistrictOfVirginia,
    "vawd": WesternDistrictOfVirginia,
    "vtd": DistrictOfVermont,
    "waed": EasternDistrictOfWashington,
    "wawd": WesternDistrictOfWashington,
    "wied": EasternDistrictOfWisconsin,
    "wiwd": WesternDistrictOfWisconsin,
    "wvnd": NorthernDistrictOfWestVirginia,
    "wvsd": SouthernDistrictOfWestVirginia,
    "wyd": DistrictOfWyoming,
    # --- state intermediate appellate courts ---
    "arizctapp": ArizonaCourtOfAppeals,
    "arkctapp": ArkansasCourtOfAppeals,
    "coloctapp": ColoradoCourtOfAppeals,
    "connappct": ConnecticutAppellateCourt,
    "delsuperct": DelawareSuperiorCourt,
    "fladistctapp": FloridaDistrictCourtOfAppeal,
    "gactapp": CourtOfAppealsOfGeorgia,
    "hawapp": IntermediateCourtOfAppealsOfHawaii,
    "idahoctapp": IdahoCourtOfAppeals,
    "illappct": IllinoisAppellateCourt,
    "indctapp": CourtOfAppealsOfIndiana,
    "iowactapp": IowaCourtOfAppeals,
    "kanctapp": KansasCourtOfAppeals,
    "kyctapp": KentuckyCourtOfAppeals,
    "lactapp": LouisianaCourtOfAppeal,
    "massappct": MassachusettsAppealsCourt,
    "mesuperct": MaineSuperiorCourt,
    "michctapp": MichiganCourtOfAppeals,
    "minnctapp": MinnesotaCourtOfAppeals,
    "missctapp": MississippiCourtOfAppeals,
    "moctapp": MissouriCourtOfAppeals,
    "ncctapp": NorthCarolinaCourtOfAppeals,
    "nebctapp": NebraskaCourtOfAppeals,
    "nevapp": NevadaCourtOfAppeals,
    "nmctapp": NewMexicoCourtOfAppeals,
    "ohioctapp": OhioCourtOfAppeals,
    "orctapp": OregonCourtOfAppeals,
    "pasuperct": PennsylvaniaSuperiorCourt,
    "prapp": PuertoRicoCourtOfAppeals,
    "scctapp": SouthCarolinaCourtOfAppeals,
    "tenncrimapp": TennesseeCourtOfCriminalAppeals,
    "tennctapp": TennesseeCourtOfAppeals,
    "texapp": TexasCourtOfAppeals,
    "texcrimapp": TexasCourtOfCriminalAppeals,
    "vactapp": CourtOfAppealsOfVirginia,
    "vtsuperct": VermontSuperiorCourt,
    "washctapp": WashingtonCourtOfAppeals,
    "wisctapp": WisconsinCourtOfAppeals,
    "wvactapp": IntermediateCourtOfAppealsOfWestVirginia,
    "mdctspecapp": AppellateCourtOfMaryland,
    "njsuperctappdiv": NewJerseySuperiorCourtAppellateDivision,
    "utahctapp": UtahCourtOfAppeals,
}


def get_extractor(court_id: str) -> BaseExtractor:
    """Return an extractor instance for ``court_id``. Falls back to the
    generic extractor (with the court id used as the label) for unknown
    courts."""
    cls = EXTRACTORS.get(court_id)
    if cls is not None:
        return cls()
    inst = GenericExtractor()
    inst.court_id = court_id
    inst.court_label = court_id
    return inst
