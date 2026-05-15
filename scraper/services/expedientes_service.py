from scraper.utils.constants import API_URL


def obtener_expedientes(page, materia=1):

    url = (
        f"{API_URL}/expedientes-autorizados"
        f"?cveMateria[]={materia}"
    )

    data = page.evaluate(
        """
        async (url) => {

            const token = localStorage.getItem("token");

            const response = await fetch(url, {

                method: "GET",

                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                }
            });

            return await response.json();
        }
        """,
        url
    )

    return data


def obtener_detalle_expediente(page, id_carpeta):

    url = (
        f"{API_URL}/portadas/obtener-carpetas-judiciales"
        f"?idCarpetaJudicial={id_carpeta}"
    )

    data = page.evaluate(
        """
        async (url) => {

            const token = localStorage.getItem("token");

            const response = await fetch(url, {

                method: "GET",

                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                }
            });

            return await response.json();
        }
        """,
        url
    )

    return data